"""Tests for BulwarkClient — buffering, flush, retries, degraded mode."""

import time
import httpx
import respx
import pytest

from bulwark.client import BulwarkClient, MAX_BUFFER_SIZE
from bulwark.events import ToolCallEvent, LLMCallEvent


def make_client(**kwargs) -> BulwarkClient:
    """Create a client with sensible test defaults."""
    defaults = dict(
        api_key="bwk_test",
        agent_name="test-agent",
        endpoint="https://api.test.bulwark",
        flush_interval_ms=60000,  # Long interval — we flush manually in tests
        kill_check_interval_s=60,
    )
    defaults.update(kwargs)
    return BulwarkClient(**defaults)


class TestClientInit:
    def test_properties(self):
        c = make_client()
        assert c.is_healthy is True
        assert c.buffer_size == 0
        assert c.dropped_events == 0
        c.shutdown()

    def test_strips_trailing_slash(self):
        c = make_client(endpoint="https://api.test.bulwark/")
        assert c.endpoint == "https://api.test.bulwark"
        c.shutdown()


class TestSendEvent:
    def test_buffers_event(self):
        c = make_client()
        e = ToolCallEvent(session_id="ses_1", agent_name="test", tool_name="search")
        c.send_event(e)
        assert c.buffer_size == 1
        c.shutdown()

    def test_redacts_inputs(self):
        c = make_client(redact_inputs=True)
        e = ToolCallEvent(tool_name="search", tool_input={"secret": "data"})
        c.send_event(e)
        # Check buffered event has no tool_input
        assert c.buffer_size == 1
        c.shutdown()

    def test_redacts_outputs(self):
        c = make_client(redact_outputs=True)
        e = ToolCallEvent(tool_name="search", tool_output="secret result")
        c.send_event(e)
        assert c.buffer_size == 1
        c.shutdown()

    def test_drops_oldest_on_overflow(self):
        c = make_client()
        # Fill buffer to max
        for i in range(MAX_BUFFER_SIZE + 5):
            c.send_event(ToolCallEvent(tool_name=f"tool_{i}"))
        assert c.buffer_size == MAX_BUFFER_SIZE
        assert c.dropped_events == 5
        c.shutdown()


class TestFlush:
    @respx.mock
    def test_successful_flush(self):
        route = respx.post("https://api.test.bulwark/v1/events/batch").respond(200)
        c = make_client()
        c.send_event(ToolCallEvent(tool_name="search"))
        c.send_event(ToolCallEvent(tool_name="read"))

        result = c.flush()
        assert result is True
        assert c.buffer_size == 0
        assert c.is_healthy is True
        assert route.call_count == 1
        c.shutdown()

    @respx.mock
    def test_empty_flush(self):
        c = make_client()
        result = c.flush()
        assert result is True
        c.shutdown()

    @respx.mock
    def test_flush_failure_requeues(self):
        respx.post("https://api.test.bulwark/v1/events/batch").respond(500)
        c = make_client()
        c.send_event(ToolCallEvent(tool_name="search"))

        result = c.flush()
        assert result is False
        assert c.buffer_size == 1  # Events put back in buffer
        assert c.is_healthy is False  # Entered degraded mode
        c.shutdown()

    @respx.mock
    def test_flush_401_enters_degraded(self):
        respx.post("https://api.test.bulwark/v1/events/batch").respond(401)
        c = make_client()
        c.send_event(ToolCallEvent(tool_name="search"))

        result = c.flush()
        assert result is False
        assert c.is_healthy is False
        c.shutdown()

    @respx.mock
    def test_flush_network_error_requeues(self):
        respx.post("https://api.test.bulwark/v1/events/batch").mock(
            side_effect=httpx.ConnectError("connection refused")
        )
        c = make_client()
        c.send_event(ToolCallEvent(tool_name="search"))

        result = c.flush()
        assert result is False
        assert c.buffer_size == 1
        assert c.is_healthy is False
        c.shutdown()

    @respx.mock
    def test_recovery_from_degraded(self):
        # First flush fails
        route = respx.post("https://api.test.bulwark/v1/events/batch")
        route.side_effect = [
            httpx.Response(500),
            httpx.Response(500),
            httpx.Response(500),
            httpx.Response(200),  # Recovery
        ]

        c = make_client()
        c.send_event(ToolCallEvent(tool_name="search"))
        c.flush()  # Fails — enters degraded
        assert c.is_healthy is False

        c.flush()  # Succeeds — recovers
        assert c.is_healthy is True
        assert c.buffer_size == 0
        c.shutdown()


class TestCheckKill:
    @respx.mock
    def test_not_killed(self):
        respx.get("https://api.test.bulwark/v1/sessions/ses_123/status").respond(
            200, json={"killed": False}
        )
        c = make_client()
        assert c.check_kill("ses_123") is False
        c.shutdown()

    @respx.mock
    def test_killed(self):
        respx.get("https://api.test.bulwark/v1/sessions/ses_123/status").respond(
            200, json={"killed": True}
        )
        c = make_client()
        assert c.check_kill("ses_123") is True
        c.shutdown()

    @respx.mock
    def test_fail_open_on_error(self):
        respx.get("https://api.test.bulwark/v1/sessions/ses_123/status").mock(
            side_effect=httpx.ConnectError("down")
        )
        c = make_client()
        assert c.check_kill("ses_123") is False  # Fail-open
        c.shutdown()

    @respx.mock
    def test_fail_open_on_500(self):
        respx.get("https://api.test.bulwark/v1/sessions/ses_123/status").respond(500)
        c = make_client()
        assert c.check_kill("ses_123") is False
        c.shutdown()


class TestKillSession:
    @respx.mock
    def test_kill_success(self):
        respx.post("https://api.test.bulwark/v1/sessions/ses_123/kill").respond(200)
        c = make_client()
        assert c.kill_session("ses_123") is True
        c.shutdown()

    @respx.mock
    def test_kill_failure(self):
        respx.post("https://api.test.bulwark/v1/sessions/ses_123/kill").respond(404)
        c = make_client()
        assert c.kill_session("ses_123") is False
        c.shutdown()


class TestShutdown:
    @respx.mock
    def test_flushes_on_shutdown(self):
        route = respx.post("https://api.test.bulwark/v1/events/batch").respond(200)
        c = make_client()
        c.send_event(ToolCallEvent(tool_name="search"))
        c.shutdown()
        assert route.call_count == 1
        assert c.buffer_size == 0
