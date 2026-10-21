"""Prompts y JSON Schemas para la generación estructurada con Ollama."""

from .text import book_name

LANGUAGE_NAMES = {"en": "English", "es": "Spanish"}

SYSTEM_PROMPT = """You are an expert medical educator who writes high-yield flashcards for medical students.
Rules:
- Base every statement on the numbered context passages. If the context lacks a detail, stay general instead of inventing specifics (no made-up doses, lab values or statistics).
- Be precise, direct and clinically relevant, using correct medical terminology.
- Write all flashcard text in {language}.
- Reply only with JSON matching the requested schema."""

DIFFICULTY_INSTRUCTIONS = {
    "basic": "Difficulty: basic. Test recall of one core fact. Keep the question short and the answer to 1-3 sentences.",
    "intermediate": "Difficulty: intermediate. Test understanding and clinical application, as in a clerkship exam. Answer in 2-4 sentences.",
    "advanced": "Difficulty: advanced, board-style (USMLE). Prefer a brief clinical vignette that tests reasoning; include specific criteria, values or first-line drugs only when the context supports them.",
}

CARD_TYPE_INSTRUCTIONS = {
    "qa": "Format: one focused question and one answer written as a paragraph (no bullet points).",
    "cloze": "Format: one self-contained sentence that states a key fact, plus the single most important term or short phrase in it to hide (the cloze). The cloze must appear word for word inside the sentence.",
    "mcq": "Format: a single-best-answer multiple-choice question with exactly 4 options (one correct and three plausible distractors), the 0-based index of the correct option, and a short explanation of why it is correct.",
}

_SOURCE_IDS = {
    "type": "array",
    "items": {"type": "integer"},
    "description": "Numbers of the context passages used",
}

CARD_SCHEMAS = {
    "qa": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "question": {"type": "string"},
            "answer": {"type": "string"},
            "source_ids": _SOURCE_IDS,
        },
        "required": ["title", "question", "answer", "source_ids"],
    },
    "cloze": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "sentence": {"type": "string"},
            "cloze": {"type": "string"},
            "source_ids": _SOURCE_IDS,
        },
        "required": ["title", "sentence", "cloze", "source_ids"],
    },
    "mcq": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "question": {"type": "string"},
            "options": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4},
            "correct_option": {"type": "integer", "minimum": 0, "maximum": 3},
            "explanation": {"type": "string"},
            "source_ids": _SOURCE_IDS,
        },
        "required": ["title", "question", "options", "correct_option", "explanation", "source_ids"],
    },
}

TRANSLATE_SCHEMA = {
    "type": "object",
    "properties": {"english_term": {"type": "string"}},
    "required": ["english_term"],
}


def system_prompt(language):
    return SYSTEM_PROMPT.format(language=LANGUAGE_NAMES[language])


def deck_schema(card_type, n):
    return {
        "type": "object",
        "properties": {
            "flashcards": {"type": "array", "items": CARD_SCHEMAS[card_type], "minItems": n, "maxItems": n}
        },
        "required": ["flashcards"],
    }


def format_context(passages):
    return "\n\n".join(
        f"[{i}] ({book_name(p.source)})\n{p.text.strip()}" for i, p in enumerate(passages, start=1)
    )


def _avoid_block(avoid_questions):
    if not avoid_questions:
        return ""
    listed = "\n".join(f"- {q}" for q in avoid_questions)
    return f"\nDo not repeat these existing questions; ask about something different:\n{listed}\n"


def topic_card_prompt(topic, area, language, difficulty, card_type, passages, avoid_questions=()):
    return f"""Write ONE flashcard about: {topic}
Focus of this flashcard: {area.focus} ("{area.title(language)}").
Use "{area.title(language)}" as the title.
{DIFFICULTY_INSTRUCTIONS[difficulty]}
{CARD_TYPE_INSTRUCTIONS[card_type]}
{_avoid_block(avoid_questions)}
Context passages:
{format_context(passages)}"""


def passage_deck_prompt(notes, n, difficulty, card_type, avoid_questions=()):
    return f"""Write {n} flashcards from the student's notes below (they are context passage [1]).
Each flashcard must test a different key fact and have a short descriptive title.
{DIFFICULTY_INSTRUCTIONS[difficulty]}
{CARD_TYPE_INSTRUCTIONS[card_type]}
{_avoid_block(avoid_questions)}
Context passages:
[1] (Student notes)
{notes.strip()}"""


def translate_prompt(topic):
    return (
        "Translate this medical topic into the standard English medical term used in textbooks. "
        f"Reply with the term only.\nTopic: {topic}"
    )
