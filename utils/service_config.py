from __future__ import annotations

SERVICE_RULES = {
    "merge": {
        "file_type": "pdf",
        "min_files": 2,
        "multi": True,
        "prompt": "\ud83d\udcce *\u062f\u0645\u062c PDF*\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641\u0627\u062a PDF \u0627\u0644\u0622\u0646.",
    },
    "split": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\u2702\ufe0f *\u062a\u0642\u0633\u064a\u0645 PDF*\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "compress": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\udddc\ufe0f *\u0636\u063a\u0637 PDF*\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "extract_text": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\udcdd *\u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0627\u0644\u0646\u0635\u0648\u0635*\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "extract_images": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\uddbc\ufe0f *\u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0627\u0644\u0635\u0648\u0631*\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "images_to_pdf": {
        "file_type": "image",
        "min_files": 1,
        "multi": True,
        "prompt": "\ud83d\uddbc\ufe0f\u27a1\ufe0f\ud83d\udcc4 *\u0635\u0648\u0631 \u0627\u0644\u0649 PDF*\n\u0623\u0631\u0633\u0644 \u0627\u0644\u0635\u0648\u0631 \u0648\u0627\u062d\u062f\u0629 \u062a\u0644\u0648 \u0627\u0644\u0623\u062e\u0631\u0649.",
    },
    "pdf_to_word": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\udcc4\u27a1\ufe0f Word\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "pdf_to_excel": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\udcca\u27a1\ufe0f Excel\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "pdf_to_images": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\uddbc\ufe0f PDF \u0627\u0644\u0649 \u0635\u0648\u0631\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "ocr": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "prompt": "\ud83d\udd0d OCR\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "encrypt_pdf": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "needs_param": "password",
        "prompt": "\ud83d\udd12 \u062d\u0645\u0627\u064a\u0629 PDF\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "decrypt_pdf": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "needs_param": "password",
        "prompt": "\ud83d\udd13 \u0625\u0632\u0627\u0644\u0629 \u062d\u0645\u0627\u064a\u0629 PDF\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "rotate_pdf": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "needs_param": "degrees",
        "prompt": "\ud83d\udd03 \u062a\u062f\u0648\u064a\u0631 \u0635\u0641\u062d\u0627\u062a\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "watermark_pdf": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "needs_param": "watermark",
        "prompt": "\ud83c\udf0a \u0639\u0644\u0627\u0645\u0629 \u0645\u0627\u0626\u064a\u0629\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "sign_pdf": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "needs_param": "signature",
        "prompt": "\u270d\ufe0f \u062a\u0648\u0642\u064a\u0639 PDF\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
    "reorder_pages": {
        "file_type": "pdf",
        "min_files": 1,
        "multi": False,
        "needs_param": "order",
        "prompt": "\ud83e\udde9 \u0625\u0639\u0627\u062f\u0629 \u062a\u0631\u062a\u064a\u0628 \u0627\u0644\u0635\u0641\u062d\u0627\u062a\n\u0623\u0631\u0633\u0644 \u0645\u0644\u0641 PDF \u0648\u0627\u062d\u062f.",
    },
}

SERVICE_KEYS = set(SERVICE_RULES.keys())
