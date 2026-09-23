import base64
import hashlib
import hmac
import json
from io import BytesIO
from unittest.mock import Mock

from homeops_agent.integrations.switchbot import (
    SwitchBotClient,
    SwitchBotConfig,
    SwitchBotError,
    run_switchbot_outlet_check,
)


class FakeResponse:
    def __init__(self, payload):
        self._buffer = BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)


def test_switchbot_signing_and_status_request():
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "statusCode": 100,
                "message": "success",
                "body": {"power": "on"},
            }
        )

    config = SwitchBotConfig(
        token="token-value",
        secret="secret-value",
        device_id="device-123",
    )
    client = SwitchBotClient(
        config,
        urlopen=fake_urlopen,
        now_ms=lambda: 1234567890123,
        nonce_factory=lambda: "nonce-value",
    )

    assert client.get_outlet_status()["power"] == "on"

    request = captured["request"]
    expected = base64.b64encode(
        hmac.new(
            b"secret-value",
            b"token-value1234567890123nonce-value",
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    assert request.full_url.endswith("/v1.1/devices/device-123/status")
    assert request.get_method() == "GET"
    assert request.headers["Authorization"] == "token-value"
    assert request.headers["Sign"] == expected
    assert request.headers["Nonce"] == "nonce-value"
    assert request.headers["T"] == "1234567890123"
    assert captured["timeout"] == 10


def test_unconfigured_switchbot_fails_closed(monkeypatch):
    monkeypatch.delenv("SWITCHBOT_TOKEN", raising=False)
    monkeypatch.delenv("SWITCHBOT_SECRET", raising=False)
    monkeypatch.delenv("SWITCHBOT_OUTLET_DEVICE_ID", raising=False)

    result = run_switchbot_outlet_check()

    assert result["configured"] is False
    assert result["ok"] is False
    assert result["action_taken"] is False
    assert result["audit_log"][0]["type"] == "provider_unconfigured"


def test_outlet_already_off_takes_no_action():
    client = Mock()
    client.get_outlet_status.return_value = {"power": "off"}

    result = run_switchbot_outlet_check(
        SwitchBotConfig("token", "secret", "device"),
        client_factory=lambda config: client,
    )

    assert result["ok"] is True
    assert result["action_taken"] is False
    client.turn_outlet_off.assert_not_called()


def test_outlet_on_uses_only_turn_off():
    client = Mock()
    client.get_outlet_status.return_value = {"power": "on"}
    client.turn_outlet_off.return_value = {}

    result = run_switchbot_outlet_check(
        SwitchBotConfig("token", "secret", "device"),
        client_factory=lambda config: client,
    )

    assert result["ok"] is True
    assert result["action_taken"] is True
    client.turn_outlet_off.assert_called_once_with()
    assert result["audit_log"][-1]["type"] == "provider_action_executed"
    assert result["audit_log"][-1]["action"] == "turn_off"


def test_unknown_power_state_blocks_action():
    client = Mock()
    client.get_outlet_status.return_value = {"deviceType": "Plug Mini (US)"}

    result = run_switchbot_outlet_check(
        SwitchBotConfig("token", "secret", "device"),
        client_factory=lambda config: client,
    )

    assert result["ok"] is False
    assert result["action_taken"] is False
    client.turn_outlet_off.assert_not_called()
    assert result["audit_log"][-1]["type"] == "provider_action_blocked"


def test_provider_failure_is_visible_and_no_action_is_claimed():
    client = Mock()
    client.get_outlet_status.side_effect = SwitchBotError("SwitchBot request failed: URLError")

    result = run_switchbot_outlet_check(
        SwitchBotConfig("token", "secret", "device"),
        client_factory=lambda config: client,
    )

    assert result["ok"] is False
    assert result["action_taken"] is False
    assert result["audit_log"][-1]["type"] == "provider_state_failed"
