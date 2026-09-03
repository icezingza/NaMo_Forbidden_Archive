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

    def get_injection_plan(self, **kwargs: Any) -> dict[str, list[dict[str, Any]]]:
        legacy_func = getattr(self.legacy, "get_injection_plan", None)
        plan = legacy_func(**kwargs) if callable(legacy_func) else {}
        if "system_pre" not in plan:
            plan["system_pre"] = []
        
        user_input = kwargs.get("user_input", "")
        ai_history = kwargs.get("ai_history", "")
        recent_ids = kwargs.get("recent_lorebook_ids", [])
        
        matches = self.fullport.match_entries(user_input, ai_history=ai_history, recent_lorebook_ids=recent_ids)
        for m in matches:
            plan["system_pre"].append({
                "id": m.entry_id,
                "content_th": m.text,
                "name": m.name_th
            })
        return plan

    def __getattr__(self, name: str) -> Any:
        # Preserve helper methods currently called on SlowBurnLorebook.
        return getattr(self.legacy, name)
