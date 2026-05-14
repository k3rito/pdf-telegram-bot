from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PIL import Image

from services.ocr.models import OCRPageResult
from services.ocr.preprocess import preprocess_image


@dataclass(slots=True)
class OCREngine:
    languages: str = "ara+eng"

    async def recognize_page(self, page_number: int, image: Image.Image) -> OCRPageResult:
        return await self._recognize_page(page_number, image)

    async def recognize_batch(self, pages: Iterable[tuple[int, Image.Image]]) -> list[OCRPageResult]:
        results: list[OCRPageResult] = []
        for page_number, image in pages:
            results.append(await self._recognize_page(page_number, image))
        return results

    async def _recognize_page(self, page_number: int, image: Image.Image) -> OCRPageResult:
        processed = preprocess_image(image)
        return await self._run_tesseract(page_number, processed.image)

    async def _run_tesseract(self, page_number: int, image: Image.Image) -> OCRPageResult:
        import pytesseract

        text = await _to_thread(pytesseract.image_to_string, image, lang=self.languages)
        confidence = _score_text(text)
        return OCRPageResult(page_number=page_number, text=text, confidence=confidence, language=self.languages)


async def _to_thread(func, *args, **kwargs):
    import asyncio

    return await asyncio.to_thread(func, *args, **kwargs)


def _score_text(text: str) -> float:
    if not text.strip():
        return 0.0
    alpha = sum(1 for char in text if char.isalpha())
    return min(1.0, alpha / max(len(text), 1))
