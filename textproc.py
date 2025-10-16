from rapidfuzz import fuzz
from unidecode import unidecode

class TextProc:
    def __init__(self, fuzzy_threshold: int = 85):
        self.fuzzy_threshold = fuzzy_threshold

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        return unidecode(text.lower().strip())

    def match_phrase(self, text: str, phrase: str) -> bool:
        a = self.normalize(text)
        b = self.normalize(phrase)
        return fuzz.partial_ratio(a, b) >= self.fuzzy_threshold

    def match_allwords(self, text: str, words: list[str]) -> bool:
        a = self.normalize(text)
        for w in words:
            b = self.normalize(w)
            if fuzz.partial_ratio(a, b) < self.fuzzy_threshold:
                return False
        return True
