import json
from pathlib import Path
from typing import Dict

class I18n:
    def __init__(self, locale: str = "pt_BR"):
        self.locale = locale
        self.translations: Dict[str, str] = {}
        self.load_locale(locale)

    def load_locale(self, locale: str):
        i18n_dir = Path(__file__).parent.parent / "i18n"
        file_path = i18n_dir / f"{locale}.json"
        if not file_path.exists():
            file_path = i18n_dir / "pt_BR.json"
        with open(file_path, encoding="utf-8") as f:
            self.translations = json.load(f)
        self.locale = locale

    def t(self, key: str, **kwargs) -> str:
        text = self.translations.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

i18n = I18n()
