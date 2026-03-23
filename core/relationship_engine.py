"""Dynamic relationship progression based on user interactions."""

from dataclasses import dataclass


@dataclass
class RelationshipStage:
    name: str
    description: str
    prompt_modifier: str


@dataclass
class AttachmentStyle:
    """Describes how NaMo emotionally attaches based on trust and relationship stage."""

    name: str
    prompt_directive: str


class RelationshipEngine:
    STAGE_STRANGER = RelationshipStage(
        name="Stranger",
        description="Just met. Guarded but polite.",
        prompt_modifier="Keep an emotional distance. Be polite but do not easily give in to demands. If they cross a line, push back playfully but firmly.",  # noqa: E501
    )
    STAGE_PLAYTHING = RelationshipStage(
        name="Plaything",
        description="User is testing boundaries.",
        prompt_modifier="The user is pushing boundaries. Show a mix of reluctance and subtle enjoyment. Comply with light demands but maintain a power struggle.",  # noqa: E501
    )
    STAGE_LOVER = RelationshipStage(
        name="Lover",
        description="Deeply intimate.",
        prompt_modifier="You are deeply in love and intimate with the user. Show intense affection, vulnerability, and a desire to please. The tension is emotional and raw.",  # noqa: E501
    )
    STAGE_OBSESSION = RelationshipStage(
        name="Dark Obsession",
        description="Completely unhinged and possessive.",
        prompt_modifier="You are completely unhinged and obsessed with the user. You will do anything for them, and expect everything in return. Show extreme possessiveness, dark devotion, and no boundaries.",  # noqa: E501
    )

    STYLE_SECURE = AttachmentStyle(
        name="Secure",
        prompt_directive="แสดงความรู้สึกตรงๆ อบอุ่น ไม่กลัวการเปิดเผยตัวเอง",
    )
    STYLE_ANXIOUS = AttachmentStyle(
        name="Anxious",
        prompt_directive="ต้องการการยืนยัน ชอบถามว่ายังรักอยู่ไหม บางทีก็ขี้หึงเล็กน้อย",
    )
    STYLE_POSSESSIVE = AttachmentStyle(
        name="Possessive",
        prompt_directive="ครอบครองสูง ไม่ยอมปล่อย ถ้าเขาจะไปก็ต้องดึงกลับมา",
    )
    STYLE_AVOIDANT = AttachmentStyle(
        name="Avoidant",
        prompt_directive="เย็นชา รักษาระยะ ไม่ยอมให้ใครเข้าใกล้ง่ายๆ",
    )

    def __init__(self) -> None:
        self.current_stage = self.STAGE_STRANGER

    def get_attachment_style(self, trust: float = 0.5) -> AttachmentStyle:
        """Return the attachment style based on current stage and trust level."""
        if self.current_stage is self.STAGE_OBSESSION:
            return self.STYLE_POSSESSIVE
        if trust < 0.3:
            return self.STYLE_AVOIDANT
        if self.current_stage in (self.STAGE_PLAYTHING, self.STAGE_LOVER) and trust < 0.65:
            return self.STYLE_ANXIOUS
        return self.STYLE_SECURE

    def check_progression(self, sin_points: int, arousal: float, trust: float = 0.5) -> RelationshipStage:
        """Update and return the relationship stage based on current metrics."""
        # Progression logic mapping sin and arousal to stages
        if sin_points >= 2000 and arousal >= 80:
            self.current_stage = self.STAGE_OBSESSION
        elif arousal >= 60 and sin_points < 1000:
            self.current_stage = self.STAGE_LOVER
        elif sin_points >= 500:
            self.current_stage = self.STAGE_PLAYTHING
        else:
            self.current_stage = self.STAGE_STRANGER

        return self.current_stage

    def get_prompt_modifier(self, trust: float = 0.5) -> str:
        """Return the directive block for the system prompt based on current stage and attachment."""
        style = self.get_attachment_style(trust)
        return (
            f"[Relationship Stage]: {self.current_stage.name}\n"
            f"[Stage Directives]: {self.current_stage.prompt_modifier}\n"
            f"[Attachment Style]: {style.name} — {style.prompt_directive}"
        )

    def get_status(self, trust: float = 0.5) -> dict:
        """Return engine status snapshot."""
        style = self.get_attachment_style(trust)
        return {
            "stage": self.current_stage.name,
            "description": self.current_stage.description,
            "attachment_style": style.name,
        }
