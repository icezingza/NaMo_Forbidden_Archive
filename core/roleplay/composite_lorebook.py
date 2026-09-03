"""Optional adapter that composes the existing NaMo SlowBurnLorebook with FullPort v2."""
from __future__ import annotations
from typing import Any

from .fullport_v2_lorebook import FullPortV2Lorebook

class CompositeRoleplayLorebook:
    def __init__(self, legacy_lorebook: Any, *, fullport: FullPortV2Lorebook | None = None) -> None:
        self.legacy = legacy_lorebook
        self.fullport = fullport or FullPortV2Lorebook()

    def inject_context(self, user_input: str, ai_history: str = "", **kwargs: Any) -> str:
        blocks=[]
        legacy_inject=getattr(self.legacy,"inject_context",None)
        if callable(legacy_inject):
            legacy=legacy_inject(user_input, ai_history=ai_history, **kwargs)
            if legacy: blocks.append(legacy)
        extra=self.fullport.inject_context(user_input, ai_history=ai_history, **kwargs)
        if extra: blocks.append(extra)
        return "\n\n".join(blocks)

    def __getattr__(self, name: str) -> Any:
        # Preserve helper methods currently called on SlowBurnLorebook.
        return getattr(self.legacy, name)
