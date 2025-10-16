from rapidfuzz import fuzz, process
from unidecode import unidecode


class TextProc:
    def __init__(self, fuzzy_threshold: int = 85):
        self.fuzzy_threshold = fuzzy_threshold

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        return unidecode(text.lower().strip())

    def fuzzy_match(self, text: str, patterns: list[str]) -> bool:
        text_norm = self.normalize(text)
        for pattern in patterns:
            pattern_norm = self.normalize(pattern)
            if fuzz.partial_ratio(pattern_norm, text_norm) >= self.fuzzy_threshold:
                return True
        return False

    def all_words_match(self, text: str, words: list[str]) -> bool:
        text_norm = self.normalize(text)
        return all(word in text_norm for word in [self.normalize(w) for w in words])
