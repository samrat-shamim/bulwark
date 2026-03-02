"""Tests for Session — lifecycle, tracking, kill switch."""

import respx
import httpx

from bulwark.client import BulwarkClient
from bulwark.session import Session


def make_client() -> BulwarkClient:
    return BulwarkClient(
        api_key="bwk_test",
        agent_name="test-agent",
        endpoint="https://api.test.bulwark",
        flush_interval_ms=60000,
        kill_check_interval_s=60,
    )


class TestSessionInit:
    def test_session_id_format(self):
        c = make_client()
        s = Session(c, name="test")
        assert s.session_id.startswith("ses_")
        assert len(s.session_id) == 16  # "ses_" + 12 hex
        assert s.name == "test"
        assert s.is_killed() is False
        assert s._event_count == 0
        c.shutdown()


class TestSessionLifecycle:
    @respx.mock
    def test_enter_sends_start_event(self):
        respx.get("https://api.test.bulwark/v1/sessions/").respond(200, json={"killed": False})
        c = make_client()
        s = Session(c, name="test")
        s.__enter__()
        # session_start event should be buffered
        assert c.buffer_size == 1
        c.shutdown()

    @respx.mock
    def test_exit_sends_end_event_and_flushes(self):
        route = respx.post("https://api.test.bulwark/v1/events/batch").respond(200)
        respx.get("https://api.test.bulwark/v1/sessions/").respond(200, json={"killed": False})

        c = make_client()
        with Session(c, name="test") as s:
            pass
        # Should have flushed (session_start + session_end)
        assert route.call_count >= 1
        c.shutdown()

    @respx.mock
    def test_context_manager_survives_api_down(self):
        respx.post("https://api.test.bulwark/v1/events/batch").mock(
            side_effect=httpx.ConnectError("down")
        )
        respx.get("https://api.test.bulwark/v1/sessions/").mock(
            side_effect=httpx.ConnectError("down")
        )

        c = make_client()
        # Should NOT raise even when API is down
        with Session(c, name="test") as s:
            s.track_tool_call("search", input={"q": "test"})
            s.track_llm_call("gpt-4", input_tokens=100)
            s.track_action("deploy", target="prod")
        c.shutdown()


class TestTracking:
    def test_track_tool_call(self):
        c = make_client()
        s = Session(c)
        s.track_tool_call("search", input={"q": "hello"}, output="results", duration_ms=100)
        assert s._event_count == 1
        assert c.buffer_size == 1
        c.shutdown()

    def test_track_llm_call(self):
        c = make_client()
        s = Session(c)
        s.track_llm_call("gpt-4", input_tokens=1000, output_tokens=500, cost_usd=0.05)
        assert s._event_count == 1
        assert c.buffer_size == 1
        c.shutdown()

    def test_track_action(self):
        c = make_client()
        s = Session(c)
        s.track_action("deploy", target="prod", metadata={"v": "1.0"})
        assert s._event_count == 1
        assert c.buffer_size == 1
        c.shutdown()

    def test_multiple_tracks(self):
        c = make_client()
        s = Session(c)
        s.track_tool_call("a")
        s.track_tool_call("b")
        s.track_llm_call("gpt-4")
        s.track_action("deploy")
        assert s._event_count == 4
        assert c.buffer_size == 4
        c.shutdown()

    def test_tracking_never_raises(self):
        """Even with a broken client, tracking should not raise."""
        c = make_client()
        s = Session(c)
        # These should all succeed silently
        s.track_tool_call("search")
        s.track_llm_call("model")
        s.track_action("action")
        assert s._event_count == 3
        c.shutdown()


class TestKillSwitch:
    def test_not_killed_by_default(self):
        c = make_client()
        s = Session(c)
        assert s.is_killed() is False
        c.shutdown()

    def test_killed_state(self):
        c = make_client()
        s = Session(c)
        s._killed = True  # Simulate kill
        assert s.is_killed() is True
        c.shutdown()
