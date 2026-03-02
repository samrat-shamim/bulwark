"""Tests for event types and serialization."""

from bulwark.events import (
    BaseEvent,
    ToolCallEvent,
    LLMCallEvent,
    ActionEvent,
    SessionStartEvent,
    SessionEndEvent,
)


class TestBaseEvent:
    def test_default_fields(self):
        e = BaseEvent()
        assert e.event_type == ""
        assert e.session_id == ""
        assert e.event_id.startswith("evt_")
        assert e.timestamp != ""
        assert e.status == "success"

    def test_to_dict_strips_none(self):
        e = BaseEvent(event_type="test", session_id="ses_123")
        d = e.to_dict()
        assert "duration_ms" not in d  # None values stripped
        assert d["event_type"] == "test"
        assert d["session_id"] == "ses_123"

    def test_to_dict_keeps_zero(self):
        e = BaseEvent(event_type="test", duration_ms=0)
        d = e.to_dict()
        assert d["duration_ms"] == 0


class TestToolCallEvent:
    def test_defaults(self):
        e = ToolCallEvent()
        assert e.event_type == "tool_call"

    def test_input_hash(self):
        e = ToolCallEvent(tool_input={"query": "hello"})
        assert e.tool_input_hash.startswith("sha256:")
        assert len(e.tool_input_hash) > 10

    def test_output_hash(self):
        e = ToolCallEvent(tool_output="result data")
        assert e.tool_output_hash.startswith("sha256:")

    def test_no_hash_when_no_input(self):
        e = ToolCallEvent()
        assert e.tool_input_hash == ""
        assert e.tool_output_hash == ""

    def test_to_dict(self):
        e = ToolCallEvent(
            session_id="ses_abc",
            agent_name="test-agent",
            tool_name="search",
            tool_input={"q": "test"},
            tool_output="results",
            duration_ms=100,
        )
        d = e.to_dict()
        assert d["event_type"] == "tool_call"
        assert d["tool_name"] == "search"
        assert d["tool_input"] == {"q": "test"}
        assert d["duration_ms"] == 100


class TestLLMCallEvent:
    def test_defaults(self):
        e = LLMCallEvent()
        assert e.event_type == "llm_call"
        assert e.input_tokens == 0
        assert e.cost_usd == 0.0

    def test_with_values(self):
        e = LLMCallEvent(
            model="gpt-4",
            provider="openai",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.05,
        )
        d = e.to_dict()
        assert d["model"] == "gpt-4"
        assert d["input_tokens"] == 1000
        assert d["cost_usd"] == 0.05


class TestActionEvent:
    def test_defaults(self):
        e = ActionEvent()
        assert e.event_type == "action"
        assert e.metadata == {}

    def test_with_metadata(self):
        e = ActionEvent(
            action="deploy",
            target="prod",
            metadata={"version": "1.0"},
        )
        d = e.to_dict()
        assert d["action"] == "deploy"
        assert d["metadata"] == {"version": "1.0"}


class TestSessionEvents:
    def test_session_start(self):
        e = SessionStartEvent(sdk_version="0.1.0", python_version="3.12.0")
        assert e.event_type == "session_start"
        d = e.to_dict()
        assert d["sdk_version"] == "0.1.0"

    def test_session_end(self):
        e = SessionEndEvent(total_events=10, total_duration_ms=5000)
        assert e.event_type == "session_end"
        d = e.to_dict()
        assert d["total_events"] == 10
        assert d["total_duration_ms"] == 5000
