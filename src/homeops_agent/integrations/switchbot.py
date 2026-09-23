"""Minimal SwitchBot OpenAPI v1.1 adapter for one low-risk outlet path."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any, Callable


API_BASE_URL = "https://api.switch-bot.com"
DEFAULT_TIMEOUT_SECONDS = 10


class SwitchBotError(RuntimeError):
    """Raised when the SwitchBot provider returns an unusable response."""


@dataclass(frozen=True)
class SwitchBotConfig:
    token: str
    secret: str
    device_id: str
    base_url: str = API_BASE_URL

    @classmethod
    def from_env(cls) -> "SwitchBotConfig | None":
        token = os.environ.get("SWITCHBOT_TOKEN", "").strip()
        secret = os.environ.get("SWITCHBOT_SECRET", "").strip()
        device_id = os.environ.get("SWITCHBOT_OUTLET_DEVICE_ID", "").strip()

        if not token or not secret or not device_id:
            return None

        return cls(token=token, secret=secret, device_id=device_id)


class SwitchBotClient:
    """Signed SwitchBot OpenAPI client scoped to one configured device."""

    def __init__(
        self,
        config: SwitchBotConfig,
        *,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        urlopen: Callable[..., Any] = urllib.request.urlopen,
        now_ms: Callable[[], int] | None = None,
        nonce_factory: Callable[[], str] | None = None,
    ) -> None:
        self.config = config
        self.timeout_seconds = timeout_seconds
        self._urlopen = urlopen
        self._now_ms = now_ms or (lambda: int(time.time() * 1000))
        self._nonce_factory = nonce_factory or (lambda: str(uuid.uuid4()))

    def _headers(self) -> dict[str, str]:
        timestamp = str(self._now_ms())
        nonce = self._nonce_factory()
        payload = f"{self.config.token}{timestamp}{nonce}".encode("utf-8")
        signature = base64.b64encode(
            hmac.new(
                self.config.secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        return {
            "Authorization": self.config.token,
            "sign": signature,
            "nonce": nonce,
            "t": timestamp,
            "Content-Type": "application/json; charset=utf8",
        }

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.base_url.rstrip('/')}{path}",
            data=body,
            headers=self._headers(),
            method=method,
        )

        try:
            with self._urlopen(request, timeout=self.timeout_seconds) as response:
                parsed = json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise SwitchBotError(f"SwitchBot request failed: {type(error).__name__}") from error

        if parsed.get("statusCode") != 100:
            message = parsed.get("message") or "provider returned non-success status"
            raise SwitchBotError(f"SwitchBot API error: {message}")

        body_value = parsed.get("body")
        return body_value if isinstance(body_value, dict) else {}

    def get_outlet_status(self) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/v1.1/devices/{self.config.device_id}/status",
        )

    def turn_outlet_off(self) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/v1.1/devices/{self.config.device_id}/commands",
            {
                "command": "turnOff",
                "parameter": "default",
                "commandType": "command",
            },
        )


def _normalize_power(status: dict[str, Any]) -> str | None:
    value = status.get("power")
    if value is None:
        value = status.get("powerState")
    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()
    if normalized in {"on", "off"}:
        return normalized
    return None


def run_switchbot_outlet_check(
    config: SwitchBotConfig | None = None,
    *,
    client_factory: Callable[[SwitchBotConfig], SwitchBotClient] = SwitchBotClient,
) -> dict[str, Any]:
    """Check one configured SwitchBot outlet and turn it off only when it is on.

    This is intentionally narrower than the simulated Good Night Check. It
    provides one real-provider proof path without broadening HomeOps permissions.
    """

    resolved = config or SwitchBotConfig.from_env()

    if resolved is None:
        return {
            "integration": "switchbot-outlet",
            "configured": False,
            "ok": False,
            "action_taken": False,
            "audit_log": [
                {
                    "type": "provider_unconfigured",
                    "device": "switchbot-outlet",
                    "reason": (
                        "SWITCHBOT_TOKEN, SWITCHBOT_SECRET, and "
                        "SWITCHBOT_OUTLET_DEVICE_ID are required."
                    ),
                }
            ],
        }

    client = client_factory(resolved)
    audit_log: list[dict[str, Any]] = []

    try:
        status = client.get_outlet_status()
    except SwitchBotError as error:
        audit_log.append(
            {
                "type": "provider_state_failed",
                "device": "switchbot-outlet",
                "reason": str(error),
            }
        )
        return {
            "integration": "switchbot-outlet",
            "configured": True,
            "ok": False,
            "action_taken": False,
            "audit_log": audit_log,
        }

    power = _normalize_power(status)
    audit_log.append(
        {
            "type": "provider_state_checked",
            "device": "switchbot-outlet",
            "power": power or "unknown",
        }
    )

    if power == "off":
        return {
            "integration": "switchbot-outlet",
            "configured": True,
            "ok": True,
            "action_taken": False,
            "power": "off",
            "audit_log": audit_log,
        }

    if power != "on":
        audit_log.append(
            {
                "type": "provider_action_blocked",
                "device": "switchbot-outlet",
                "reason": "Outlet power state was missing or unsupported; no action was sent.",
            }
        )
        return {
            "integration": "switchbot-outlet",
            "configured": True,
            "ok": False,
            "action_taken": False,
            "power": power or "unknown",
            "audit_log": audit_log,
        }

    try:
        client.turn_outlet_off()
    except SwitchBotError as error:
        audit_log.append(
            {
                "type": "provider_action_failed",
                "device": "switchbot-outlet",
                "action": "turn_off",
                "reason": str(error),
            }
        )
        return {
            "integration": "switchbot-outlet",
            "configured": True,
            "ok": False,
            "action_taken": False,
            "power": "on",
            "audit_log": audit_log,
        }

    audit_log.append(
        {
            "type": "provider_action_executed",
            "device": "switchbot-outlet",
            "action": "turn_off",
        }
    )
    return {
        "integration": "switchbot-outlet",
        "configured": True,
        "ok": True,
        "action_taken": True,
        "previous_power": "on",
        "requested_power": "off",
        "audit_log": audit_log,
    }
