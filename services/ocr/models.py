from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class OCRPageResult:
    page_number: int
    text: str
    confidence: float = 0.0
    language: str = "ara+eng"


@dataclass(slots=True)
class OCRDocumentResult:
    pages: list[OCRPageResult] = field(default_factory=list)

    @property
    def combined_text(self) -> str:
        return "\n".join(f"── OCR صفحة {page.page_number} ──\n{page.text.strip()}" for page in self.pages).strip()

    @property
    def average_confidence(self) -> float:
        if not self.pages:
            return 0.0
        return sum(page.confidence for page in self.pages) / len(self.pages)
