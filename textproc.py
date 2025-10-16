import re
from typing import List
from rapidfuzz import fuzz
from unidecode import unidecode


_WORD = re.compile(r"\w+", re.UNICODE)


class TextProc:
def __init__(self, fuzzy_threshold: int = 85):
self.th = fuzzy_threshold


def normalize(self, text: str) -> str:
"""Нижній регістр, ASCII-транслитерація для лат/кирилиці, прибрати зайве, стиск пробілів."""
if not text:
return ""
t = text.lower()
t = unidecode(t) # перетворює кирилицю на латиницю, прибирає діакритику
# якщо у вашому оточенні re не підтримує \p{P}\p{S}, використайте альтернативний рядок нижче
t = re.sub(r"[\p{P}\p{S}]", " ", t)
# альтернативний варіант: t = re.sub(r"[^\w\s]", " ", t)
t = re.sub(r"\s+", " ", t).strip()
return t


def fuzzy_contains(self, haystack: str, needle: str) -> bool:
"""Перевіряє, чи рядок містить підрядок з урахуванням опечаток (partial_ratio)."""
if not haystack or not needle:
return False
score = fuzz.partial_ratio(haystack, needle)
return score >= self.th


def match_phrase(self, text: str, phrase: str) -> bool:
return self.fuzzy_contains(self.normalize(text), self.normalize(phrase))


def match_allwords(self, text: str, words: List[str]) -> bool:
base = self.normalize(text)
for w in words:
if not self.fuzzy_contains(base, self.normalize(w)):
return False
return True
