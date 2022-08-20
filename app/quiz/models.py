from dataclasses import dataclass
from typing import Optional


@dataclass
class Theme:
    id: Optional[int]
    title: str


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: str


@dataclass
class Answer:
    title: str
    is_correct: bool

