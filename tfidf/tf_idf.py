from math import *


class TermsStatistics:
	document_id_to_word_count_map: dict[int, dict[str, int]]
	documents_words: set[str]

	def __init__(self, document_id_to_word_count_map: dict[int, dict[str, int]]):
		self.document_id_to_word_count_map = document_id_to_word_count_map
		self.documents_words = set(
			word
			for word_count_map in document_id_to_word_count_map.values()
			for word in word_count_map.keys())


class TfIdf:
	idf: dict[str, float]
	tf_idf: dict[int, dict[str, float]]

	def __init__(self, idf: dict[str, float], tf_idf: dict[int, dict[str, float]]):
		self.idf = idf
		self.tf_idf = tf_idf


class TfIdfCalculator:
	def calculate(self, terms: TermsStatistics) -> TfIdf:
		documents_count: int = len(terms.document_id_to_word_count_map.keys())
		idf: dict[str, float] = {
			word: log(
				float(documents_count)
				/ sum(
					1
					for word_count_map in terms.document_id_to_word_count_map.values()
					if word in word_count_map))
			for word in terms.documents_words}

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
				word: tf_value * idf[word]
				for word, tf_value in tf[document_id].items()}

		return TfIdf(idf, tf_idf)