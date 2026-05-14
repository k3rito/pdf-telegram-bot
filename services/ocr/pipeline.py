from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable

from PIL import Image

from services.ocr.engine import OCREngine
from services.ocr.models import OCRDocumentResult, OCRPageResult


@dataclass(slots=True)
class OCRPipeline:
    engine: OCREngine
    max_concurrency: int = 2

    async def run(self, pages: Iterable[tuple[int, Image.Image]]) -> OCRDocumentResult:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def recognize(page_number: int, image: Image.Image) -> OCRPageResult:
            async with semaphore:
                return await self.engine.recognize_page(page_number, image)

        tasks = [asyncio.create_task(recognize(page_number, image)) for page_number, image in pages]
        results = await asyncio.gather(*tasks)
        return OCRDocumentResult(pages=list(results))
