"""Modelos de entrada y salida de la API."""

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

CardType = Literal["qa", "cloze", "mcq"]
Difficulty = Literal["basic", "intermediate", "advanced"]
Language = Literal["en", "es"]
Mode = Literal["topic", "passage"]

MAX_TOPIC_CHARS = 200
MAX_PASSAGE_CHARS = 12000


class GenerateRequest(BaseModel):
    texto: str = Field(min_length=1)
    mode: Mode = "topic"
    card_type: CardType = "qa"
    difficulty: Difficulty = "intermediate"
    language: Language = "en"
    num_cards: int = Field(default=5, ge=1, le=10)

    @field_validator("texto")
    @classmethod
    def _strip(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("El texto no puede estar vacío")
        return value

    @model_validator(mode="after")
    def _check_length(self):
        limit = MAX_TOPIC_CHARS if self.mode == "topic" else MAX_PASSAGE_CHARS
        if len(self.texto) > limit:
            hint = (
                " Para generar tarjetas a partir de un texto largo usa el modo 'passage'."
                if self.mode == "topic"
                else ""
            )
            raise ValueError(f"El texto supera {limit} caracteres.{hint}")
        return self


class RegenerateRequest(GenerateRequest):
    area: Optional[str] = None
    avoid_questions: list[str] = Field(default_factory=list, max_length=20)


class Source(BaseModel):
    book: str
    chunk_id: Optional[int] = None
    excerpt: str


class Support(BaseModel):
    score: float
    supported: bool


class Flashcard(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    card_type: CardType = "qa"
    area: Optional[str] = None
    title: str
    question: str
    answer: str
    options: Optional[list[str]] = None
    correct_option: Optional[int] = None
    explanation: Optional[str] = None
    cloze_sentence: Optional[str] = None
    cloze: Optional[str] = None
    sources: list[Source] = Field(default_factory=list)
    support: Optional[Support] = None


class ExportRequest(BaseModel):
    deck_name: str = Field(default="Medical Flashcards", min_length=1, max_length=120)
    cards: list[Flashcard] = Field(min_length=1, max_length=2000)
