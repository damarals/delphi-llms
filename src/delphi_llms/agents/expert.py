from dataclasses import dataclass


@dataclass(frozen=True)
class ExpertConfig:
    expert_id: str
    seed: int
