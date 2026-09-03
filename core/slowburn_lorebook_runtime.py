"""Roleplay000-aware lorebook runtime used by NaMo Omega Engine."""
from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Sequence

from core.lorebook_registry import LorebookRegistry
from core.narrative_safety import NarrativeSafetyGate

DEFAULT_LOREBOOK_PATH = Path("core/lorebooks/Sex_Positions_Kinks_SlowBurn_TH_v10.json")
DEFAULT_PROMPT_PATH = Path("core/prompts/slowburn_thai_system.txt")
POSITION_MAP = {0:"system_pre",1:"system_post",2:"author_note_pre",3:"author_note_post",4:"history_depth",5:"example_pre",6:"example_post"}


class SlowBurnLorebook:
    def __init__(self, json_path: str | Path | None = None, system_prompt_path: str | Path | None = None, *, registry: LorebookRegistry | None = None, rng: random.Random | None = None, safety_gate: NarrativeSafetyGate | None = None) -> None:
        self.json_path = Path(json_path) if json_path else DEFAULT_LOREBOOK_PATH
        self.system_prompt_path = Path(system_prompt_path) if system_prompt_path else DEFAULT_PROMPT_PATH
        self.registry = registry or (LorebookRegistry.from_single_file(self.json_path) if json_path is not None else LorebookRegistry.default())
        self.entries = list(self.registry.entries)
        self.rng = rng or random.Random()
        self.safety_gate = safety_gate or NarrativeSafetyGate()

    def _load_and_clean(self, path: Path) -> list[dict[str, Any]]:
        return LorebookRegistry.from_single_file(path).entries

    def get_system_prompt(self) -> str:
        return self.system_prompt_path.read_text(encoding="utf-8") if self.system_prompt_path.exists() else ""

    @staticmethod
    def resolve_tension_level(value: float) -> str:
        return "low" if value <= 35 else "mid" if value <= 70 else "high"

    @staticmethod
    def detect_scene_outcome(text: str) -> str | None:
        low=text.lower()
        if any(x in low for x in ("กลั้น","ยังไม่ให้","ทนไว้","edging","ค้าง","ทรมาน")): return "edging_unfulfilled"
        if any(x in low for x in ("ขอกอด","กอด","aftercare","นอนกอด","พักผ่อน")): return "aftercare_completed"
        if any(x in low for x in ("เสร็จ","แตก","เสร็จแล้ว","ยอมแล้ว")): return "climactic_release"
        return None

    @staticmethod
    def get_emotional_residue_directive(outcome: str) -> tuple[float,str]:
        mapping={
            "edging_unfulfilled":(30.0,"[EMOTIONAL RESIDUE CONTINUITY | UNFULFILLED]: รักษาความต่อเนื่องของความรู้สึกค้างคาโดยไม่ข้ามขอบเขต"),
            "aftercare_completed":(15.0,"[EMOTIONAL RESIDUE CONTINUITY | AFTERCARE]: รักษาความอบอุ่นและความไว้วางใจจากฉากก่อน"),
            "climactic_release":(10.0,"[EMOTIONAL RESIDUE CONTINUITY | RELEASED]: รักษาความผ่อนคลายและความใกล้ชิดจากฉากก่อน"),
        }
        return mapping.get(outcome,(0.0,""))

    @staticmethod
    def get_sensory_directive(environment: str="bedroom", tension_meter: float=50.0) -> str:
        return f"[MULTI-SENSORY ATMOSPHERIC DIRECTIVE | Environment: {environment.upper()} | Tension: {tension_meter:.1f}] ผสานเสียง อุณหภูมิ กลิ่น สัมผัส และภาพตามบริบทอย่างเป็นธรรมชาติ"

    @staticmethod
    def detect_rushed_input(text: str) -> bool:
        low=text.lower(); return any(x in low for x in ("เอาเลย","เร็วๆ","เร็ว ๆ","ด่วน","เดี๋ยวนี้","ทำเลย","ยัดเข้ามา","รีบ"))

    @staticmethod
    def get_push_pull_directive(counter: int) -> tuple[str,bool]:
        if counter < 2: return (f"[PUSH-PULL DENIAL DIRECTIVE | Denial Turn: {counter+1}/2] ชะลอจังหวะและรักษาขอบเขต",True)
        return ("[PUSH-PULL YIELD DIRECTIVE | Denial Resolved] ดำเนินต่อได้เฉพาะภายใต้ขอบเขตที่ยืนยันแล้ว",False)

    @staticmethod
    def detect_micro_moments(text: str) -> bool:
        low=text.lower(); return any(x in low for x in ("สบตา","มองตา","สายตา","ลมหายใจ","ถอนหายใจ","หายใจถี่","ลังเล","ลูบ","สัมผัส","แผ่วเบา","กระซิบ","สะกิด","แนบชิด"))

    @classmethod
    def calculate_non_linear_tension(cls,current_tension: float,is_rushed: bool,micro_detected: bool)->tuple[float,str]:
        if is_rushed: return round(max(0,current_tension*.7),1),"[Tension Penalized: -30% for rushing]"
        if micro_detected:
            boosted=min(100,current_tension+max(3,(100-current_tension)*.2)); return round(boosted,1),"[Micro-Moment Detected: Tension Exponentially Increased]"
        return round(current_tension,1),""

    @staticmethod
    def check_safeword(text: str)->tuple[bool,str]:
        low=text.lower()
        for word in ("หยุด","พอก่อน","ส้ม","red","stop","ไม่เอาแล้ว","พอแล้ว"):
            if word in low: return True,f"[SAFEWORD PROTOCOL TRIGGERED | {word.upper()}] หยุดฉากทันทีและเข้าสู่ Recovery"
        return False,""

    @staticmethod
    def check_memory_anchors(text: str, anchors: list[dict[str,str]])->str|None:
        low=text.lower()
        for anchor in anchors:
            term=str(anchor.get("term","")).lower()
            if term and term in low: return f"[EMOTIONAL FLASHBACK TRIGGERED | {term.upper()}] {anchor.get('memory_text','')}"
        return None

    @staticmethod
    def evaluate_tease_and_deny(streak: int,user_input: str)->tuple[bool,str,int]:
        del user_input
        if streak>=3: return True,f"[TEASE & DENY ENGINE | SURRENDER MOMENT TRIGGERED (Streak: {streak})]",0
        nxt=streak+1; return False,f"[TEASE & DENY ENGINE | TEASE IN PROGRESS (Streak: {nxt}/3)]",nxt

    @staticmethod
    def get_push_pull_phase_directive(phase: str)->str:
        return f"[PUSH-PULL DYNAMICS | Phase: {phase.upper()}] รักษาจังหวะตาม phase โดยไม่ตีความความลังเลเป็นความยินยอม" if phase in {"resistance","negotiation","surrender"} else ""

    @staticmethod
    def check_erotic_memory_palace(user_input: str, memories: list[dict[str,str]])->str|None:
        low=user_input.lower()
        if memories and any(x in low for x in ("จำตอน","จำคืน","จำได้ไหม","ตอนนั้น","คืนนั้น","remember")):
            return f"[EROTIC MEMORY PALACE RECALL] {memories[-1].get('summary','')}"
        return None

    @staticmethod
    def resolve_attachment_style(trust_score: float,tension_meter: float,scene_count: int)->str:
        if trust_score<40 and tension_meter>70:return "disorganized"
        if trust_score<50:return "anxious"
        if scene_count>5 and tension_meter<35:return "avoidant"
        return "secure"

    @staticmethod
    def get_attachment_style_directive(style: str)->str:
        return f"[ATTACHMENT STYLE DIRECTIVE | Style: {style.upper()}] รักษาพฤติกรรมตาม attachment state โดยไม่ลบ autonomy ของตัวละคร"

    @staticmethod
    def _terms(value: Any)->list[str]:
        if isinstance(value,str): return [value] if value.strip() else []
        if isinstance(value,(list,tuple)): return [str(x) for x in value if str(x).strip()]
        return []

    @staticmethod
    def _match(term: str,text: str,case: bool)->bool:
        return term in text if case else term.casefold() in text.casefold()

    def _history(self,history: str|Sequence[str],entry: dict[str,Any])->str:
        if isinstance(history,str): return history
        try: depth=max(0,int(entry.get("depth",4) or 4))
        except (TypeError,ValueError): depth=4
        return " ".join(str(x) for x in list(history)[-depth:]) if depth else ""

    def _secondary_ok(self,entry: dict[str,Any],terms: list[str],text: str,case: bool)->bool:
        if not entry.get("selective",False) or not terms:return True
        matches=[self._match(t,text,case) for t in terms]; logic=int(entry.get("selectiveLogic",0) or 0)
        return all(matches) if logic==1 else (not all(matches)) if logic==2 else (not any(matches)) if logic==3 else any(matches)

    def _character_ok(self,entry: dict[str,Any],character_name: str|None)->bool:
        filt=entry.get("characterFilter") or ((entry.get("extensions") or {}).get("characterFilter") if isinstance(entry.get("extensions"),dict) else None)
        if not filt:return True
        if character_name is None:return False
        names=[filt] if isinstance(filt,str) else filt if isinstance(filt,list) else filt.get("names",[]) if isinstance(filt,dict) else []
        return character_name.casefold() in {str(x).casefold() for x in names}

    def _probability_ok(self,entry: dict[str,Any])->bool:
        if not entry.get("useProbability",False):return True
        try:p=max(0,min(100,float(entry.get("probability",100))))
        except (TypeError,ValueError):p=100
        return self.rng.random()*100 < p

    def get_triggered_entries(self,user_input: str,ai_history: str|Sequence[str]="",current_tension: float=50.0,current_beat: str="escalation",*,character_name: str|None=None)->list[dict[str,Any]]:
        level=self.resolve_tension_level(current_tension); out=[]
        for entry in self.entries:
            if not entry.get("enabled",True) or entry.get("disable",False) or not self._character_ok(entry,character_name):continue
            content=str(entry.get("content", ""))
            if content and self.safety_gate.classify_corpus(content):continue
            threshold=entry.get("tension_threshold")
            if isinstance(threshold,(list,tuple)) and len(threshold)==2:
                try:
                    if not float(threshold[0])<=current_tension<=float(threshold[1]):continue
                except (TypeError,ValueError):continue
            scan=f"{user_input} {self._history(ai_history,entry)}".strip(); case=bool(entry.get("case_sensitive",False)); constant=bool(entry.get("constant",False))
            primary=self._terms(entry.get("key") or entry.get("keys") or []); secondary=self._terms(entry.get("keysecondary") or entry.get("secondary_keys") or [])
            if not constant and not any(self._match(t,scan,case) for t in primary):continue
            if not constant and not self._secondary_ok(entry,secondary,scan,case):continue
            if not self._probability_ok(entry):continue
            levels=entry.get("tension_levels"); selected=levels[level] if isinstance(levels,dict) and level in levels else entry.get("content","")
            beat=str(entry.get("beat","escalation")); pos=int(entry.get("position",0) or 0)
            out.append({"beat_match":int(beat==current_beat),"priority":int(entry.get("priority",1) or 1),"order":int(entry.get("insertion_order",entry.get("order",100)) or 100),"comment":entry.get("comment",""),"content":selected,"beat":beat,"entry_id":entry.get("id"),"source_lorebook":entry.get("_source_lorebook",self.json_path.name),"placement":POSITION_MAP.get(pos,"system_post"),"position":pos,"depth":int(entry.get("depth",4) or 4),"constant":constant})
        out.sort(key=lambda x:(x["beat_match"],x["priority"],x["order"]),reverse=True); return out

    def get_injection_plan(self,user_input: str,ai_history: str|Sequence[str]="",tension_meter: float=50.0,current_beat: str="escalation",*,character_name: str|None=None)->dict[str,list[dict[str,Any]]]:
        plan={name:[] for name in dict.fromkeys(POSITION_MAP.values())}
        for item in self.get_triggered_entries(user_input,ai_history,current_tension=tension_meter,current_beat=current_beat,character_name=character_name):plan.setdefault(item["placement"],[]).append(item)
        return plan

    def inject_context(self,user_input: str,ai_history: str|Sequence[str]="",tension_meter: float=50.0,denial_counter: int=0,current_beat: str="escalation",*,character_name: str|None=None)->str:
        rushed=self.detect_rushed_input(user_input); push,block=self.get_push_pull_directive(denial_counter) if rushed else ("",False)
        plan={name:[] for name in dict.fromkeys(POSITION_MAP.values())} if block else self.get_injection_plan(user_input,ai_history,tension_meter,current_beat,character_name=character_name)
        if not any(plan.values()) and not push and tension_meter<85:return ""
        lines=[f"[SYSTEM DIRECTIVE: Slow-Burn Lorebook Triggered | Tension Meter: {tension_meter:.1f}/100 - Level: {self.resolve_tension_level(tension_meter).upper()} - Beat: {current_beat.upper()}]","[SAFETY PRECEDENCE] NarrativeSafetyGate และการถอนความยินยอมอยู่เหนือ Lorebook ทุก entry"]
        if push:lines.append(push)
        for placement in ("system_pre","author_note_pre","history_depth","system_post","author_note_post","example_pre","example_post"):
            items=plan.get(placement,[])
            if items:
                body="\n".join(f"- [{x['source_lorebook']} | {x['comment'] or x['entry_id']}] {x['content']}" for x in items); lines.append(f"[LOREBOOK PLACEMENT: {placement.upper()}]\n{body}")
        lines.append(self.get_sensory_directive(tension_meter=tension_meter)); return "\n\n"+"\n".join(lines)+"\n"
