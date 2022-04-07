from math import sqrt
from typing import Iterable, Tuple

from common.common import count_duplicates, scalar_product
from tfidf.tf_idf import TermsStatistics, TfIdf, TfIdfCalculator


class VectorSearch:
	__query_document_id: int = -1
	__distance_threshold: float = 1

	class __Document:
		def __init__(self, id_: int, tf_idf: dict[str, float], corpus_words: list[str]):
			self.id_: int = id_
			self.vector: list[float] = [tf_idf.get(word, 0) for word in corpus_words]
			self.vector_length: float = sqrt(scalar_product(self.vector, self.vector))

	def __init__(self, tf_idf: TfIdf, tf_idf_calculator: TfIdfCalculator):
		self.tf_idf: TfIdf = tf_idf
		self.corpus_words: list[str] = list(tf_idf.idf.keys())
		self.tf_idf_calculator: TfIdfCalculator = tf_idf_calculator

		self.documents: list[VectorSearch.__Document] = [
			VectorSearch.__Document(document_id, document_tf_idf, self.corpus_words)
			for document_id, document_tf_idf in tf_idf.tf_idf.items()]

	def search(self, query_terms: list[str]) -> dict[int, float]:
		query_terms_count: dict[str, int] = count_duplicates(query_terms)
		query_tf_idf: TfIdf = self.tf_idf_calculator.calculate(
			TermsStatistics({self.__query_document_id: query_terms_count}),
			self.tf_idf.idf)
		query_document: VectorSearch.__Document = VectorSearch.__Document(
			self.__query_document_id,
			query_tf_idf.tf_idf[self.__query_document_id],
			self.corpus_words)
		if query_document.vector_length <= 0:
			return {}

		result_documents: Iterable[Tuple[VectorSearch.__Document, float]] = sorted(
			{
				document: self.__calculate_distance(document, query_document)
				for document in self.documents}
				.items(),
			key = lambda x: x[1])
		result_documents = filter(lambda x: x[1] < self.__distance_threshold, result_documents)
		return {
			document.id_: distance
			for document, distance in result_documents}

	@staticmethod
	def __calculate_distance(first: __Document, second: __Document) -> float:
		return 1 - scalar_product(first.vector, second.vector) / (first.vector_length * second.vector_length)
