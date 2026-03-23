"""Dynamic relationship progression based on user interactions."""

from dataclasses import dataclass


@dataclass
class RelationshipStage:
    name: str
    description: str
    prompt_modifier: str


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

    def __init__(self) -> None:
        self.current_stage = self.STAGE_STRANGER

    def check_progression(self, sin_points: int, arousal: float) -> RelationshipStage:
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

    def get_prompt_modifier(self) -> str:
        """Return the directive block for the system prompt based on current stage."""
        return (
            f"[Relationship Stage]: {self.current_stage.name}\n"
            f"[Stage Directives]: {self.current_stage.prompt_modifier}"
        )

    def get_status(self) -> dict:
        """Return engine status snapshot."""
        return {"stage": self.current_stage.name, "description": self.current_stage.description}
