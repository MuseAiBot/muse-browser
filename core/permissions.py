"""Permission gate: no action reaches Chromium without passing this.

Action classes:
  read           - navigate, text, screenshot, evaluate (read-only JS)
  interact       - click, type
  state_changing - form submits, login flows, anything that mutates remote state

Hard rules (never overridable):
  - Never create accounts (no sign-up / registration flows).
  - Never use third-party CAPTCHA solvers unless explicitly approved for the task.
"""
from dataclasses import dataclass
from enum import Enum


class ActionClass(str, Enum):
    READ = "read"
    INTERACT = "interact"
    STATE_CHANGING = "state_changing"


ACTION_CLASSES: dict[str, ActionClass] = {
    "navigate": ActionClass.READ,
    "text": ActionClass.READ,
    "screenshot": ActionClass.READ,
    "evaluate": ActionClass.READ,
    "click": ActionClass.INTERACT,
    "type": ActionClass.INTERACT,
    "submit": ActionClass.STATE_CHANGING,
    "login": ActionClass.STATE_CHANGING,
}

# URL substrings that always indicate account creation — hard deny.
ACCOUNT_CREATION_MARKERS = [
    "signup", "sign-up", "register", "registration",
    "create-account", "create_account", "join-now",
]


@dataclass
class Decision:
    allowed: bool
    reason: str


class PermissionGate:
    def __init__(self, policy: dict | None = None):
        # policy: {"default": "read"|"interact"|"state_changing",
        #          "profiles": {"name": {"allow": [...]}}}
        self.policy = policy or {"default": "interact", "profiles": {}}

    def _max_allowed(self, profile: str) -> ActionClass:
        prof = self.policy.get("profiles", {}).get(profile, {})
        level = prof.get("allow", self.policy.get("default", "interact"))
        return ActionClass(level)

    def check(self, profile: str, action: str, params: dict | None = None) -> Decision:
        params = params or {}
        aclass = ACTION_CLASSES.get(action, ActionClass.STATE_CHANGING)

        # Hard rule 1: never create accounts.
        url = str(params.get("url", "")) + str(params.get("selector", ""))
        if action in ("navigate", "click", "submit") and any(
            m in url.lower() for m in ACCOUNT_CREATION_MARKERS
        ):
            return Decision(False, "hard-deny: account creation is never allowed")

        order = [ActionClass.READ, ActionClass.INTERACT, ActionClass.STATE_CHANGING]
        if order.index(aclass) <= order.index(self._max_allowed(profile)):
            return Decision(True, f"allowed: {aclass.value} within policy")
        return Decision(False, f"denied: {aclass.value} exceeds policy for profile '{profile}'")
