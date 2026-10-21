"""Áreas que cubre el set de flashcards de un tema.

Cada área tiene su propia consulta de recuperación, de modo que cada tarjeta se
genera con fragmentos específicos (fisiopatología, diagnóstico, tratamiento…) en
lugar de compartir 5 fragmentos recuperados con el nombre de la enfermedad.

`medquad_prefixes` relaciona cada área con los tipos de pregunta de MedQuAD,
que se usan como referencia en la evaluación (pln_model/evaluation).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Area:
    key: str
    title_en: str
    title_es: str
    focus: str
    query_template: str
    medquad_prefixes: tuple

    def title(self, language):
        return self.title_es if language == "es" else self.title_en

    def query(self, topic):
        return self.query_template.format(topic=topic)


AREAS = (
    Area(
        key="definition",
        title_en="Definition & Pathophysiology",
        title_es="Definición y fisiopatología",
        focus="the core definition and the underlying pathophysiological mechanisms",
        query_template="{topic} definition pathophysiology mechanism",
        medquad_prefixes=("what is (are)", "what is"),
    ),
    Area(
        key="etiology",
        title_en="Etiology & Risk Factors",
        title_es="Etiología y factores de riesgo",
        focus="the causes and predisposing risk factors",
        query_template="{topic} causes etiology risk factors",
        medquad_prefixes=("what causes",),
    ),
    Area(
        key="clinical",
        title_en="Clinical Presentation",
        title_es="Presentación clínica",
        focus="the signs, symptoms and clinical manifestations",
        query_template="{topic} signs symptoms clinical presentation",
        medquad_prefixes=("what are the symptoms of",),
    ),
    Area(
        key="diagnosis",
        title_en="Diagnostic Approach",
        title_es="Abordaje diagnóstico",
        focus="the key diagnostic tests, criteria and differential diagnosis",
        query_template="{topic} diagnosis tests criteria differential diagnosis",
        medquad_prefixes=("how to diagnose",),
    ),
    Area(
        key="treatment",
        title_en="Management & Treatment",
        title_es="Manejo y tratamiento",
        focus="the management, therapeutic interventions and prognosis",
        query_template="{topic} treatment management therapy prognosis",
        medquad_prefixes=("what are the treatments for",),
    ),
)

AREAS_BY_KEY = {area.key: area for area in AREAS}
