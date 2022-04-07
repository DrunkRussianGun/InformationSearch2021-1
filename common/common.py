import re as regex
from typing import Iterable


def delete_extra_whitespaces(text):
	text = text.strip()

	# Заменяем каждую последовательность пробельных символов на единственный пробел,
	# за исключением переносов строк
	text = regex.sub("((?!\\n)\\s)+", " ", text)
	# Убираем пробельные символы вокруг переносов строк
	# и заменяем каждую последовательность переносов строк на единственный перенос строки
	text = regex.sub("\\s*\\n\\s*", "\n", text)

	return text


def count_duplicates(elements: Iterable[str]) -> dict[str, int]:
	counts: dict[str, int] = {}
	for element in elements:
		counts.setdefault(element, 0)
		counts[element] += 1
	return counts


def scalar_product(vector1: list[float], vector2: list[float]) -> float:
	return sum(map(lambda first, second: first * second, vector1, vector2))
