from __future__ import annotations

from config import DEFAULT_LANG

LANG = {
    "ar": {
        "welcome": "\ud83d\udc4b *\u0645\u0631\u062d\u0628\u0627\u064b \u0628\u0643 \u0641\u064a \u0628\u0648\u062a PDF!*\n\n\u0627\u062e\u062a\u0631 \u0627\u0644\u062e\u062f\u0645\u0629 \u0627\u0644\u062a\u064a \u062a\u0631\u064a\u062f\u0647\u0627:",
        "help": "\u2139\ufe0f \u0627\u0633\u062a\u062e\u062f\u0645 @pdf \u062b\u0645 \u0627\u062e\u062a\u0631 \u062e\u062f\u0645\u0629 \u0623\u0648 \u0627\u0631\u0633\u0644 \u0627\u0644\u0645\u0644\u0641. \u0639\u0646\u062f \u0627\u0643\u062a\u0645\u0627\u0644 \u0627\u0644\u0631\u0641\u0639 \u0627\u0636\u063a\u0637 \"\u0628\u062f\u0621 \u0627\u0644\u0645\u0639\u0627\u0644\u062c\u0629\".",
        "cancel": "\u274c \u062a\u0645 \u0627\u0644\u0625\u0644\u063a\u0627\u0621. \u0627\u062e\u062a\u0631 \u062e\u062f\u0645\u0629 \u0623\u062e\u0631\u0649:",
        "lang_set": "\u2705 \u062a\u0645 \u062a\u0639\u064a\u064a\u0646 \u0627\u0644\u0644\u063a\u0629: {lang}",
        "lang_help": "\u0627\u0633\u062a\u062e\u062f\u0645: @pdf lang ar \u0623\u0648 @pdf lang en",
    },
    "en": {
        "welcome": "\ud83d\udc4b *Welcome to PDF Bot!*\n\nChoose a service:",
        "help": "\u2139\ufe0f Use @pdf, choose a service, then send the file. When done, press \"Start processing\".",
        "cancel": "\u274c Cancelled. Choose another service:",
        "lang_set": "\u2705 Language set to: {lang}",
        "lang_help": "Use: @pdf lang ar or @pdf lang en",
    },
}


def t(key: str, lang: str | None = None) -> str:
    use_lang = lang or DEFAULT_LANG
    return LANG.get(use_lang, LANG[DEFAULT_LANG]).get(key, key)
