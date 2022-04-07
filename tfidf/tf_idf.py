from math import *
from typing import *


class TermsStatistics:
	def __init__(self, document_id_to_word_count_map: dict[int, dict[str, int]]):
		self.document_id_to_word_count_map: dict[int, dict[str, int]] = document_id_to_word_count_map
		self.corpus_words: list[str] = list(
			set(
				word
				for word_count_map in document_id_to_word_count_map.values()
				for word in word_count_map.keys()))


class TfIdf:
	def __init__(self, idf: dict[str, float], tf_idf: dict[int, dict[str, float]]):
		self.idf: dict[str, float] = idf
		self.tf_idf: dict[int, dict[str, float]] = tf_idf


class TfIdfCalculator:
	def calculate(self, terms: TermsStatistics, idf: Optional[dict[str, float]] = None) -> TfIdf:
		if idf is None:
			documents_count: int = len(terms.document_id_to_word_count_map.keys())
			idf = {
				word: log(
					float(documents_count)
					/ sum(
						1
						for word_count_map in terms.document_id_to_word_count_map.values()
						if word in word_count_map))
				for word in terms.corpus_words}

		tf: dict[int, dict[str, float]] = {}
		tf_idf: dict[int, dict[str, float]] = {}
		document_id: int
		word_count_map: dict[str, int]
		for document_id, word_count_map in terms.document_id_to_word_count_map.items():
			document_words_count = sum(word_count_map.values())
			tf[document_id] = {
				word: float(count) / document_words_count
				for word, count in word_count_map.items()}
			tf_idf[document_id] = {
				word: tf_value * idf.get(word, 0)
				for word, tf_value in tf[document_id].items()}

		return TfIdf(idf, tf_idf)
