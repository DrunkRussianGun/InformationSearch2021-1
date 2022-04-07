from alphabet_detector import *

from common.infrastructure import *
from crawling.raw_document import *
from tfidf.tf_idf_repository import *
from tokenization.tokenizer import *
from vectorsearch.vector_search import *

log = logging.getLogger()


def main():
	configure_logging()

	run()


def run():
	log.info("Загружаю страницы")
	pages_repository: RawDocumentRepository = RawDocumentRepository(raw_texts_repository_name)
	page_ids = pages_repository.get_all_ids()
	page_urls: dict[int, str] = {
		page_id: pages_repository.get(page_id).url
		for page_id in page_ids}

	log.info("Загружаю рассчитанные значения TF–IDF")
	tf_idf_repository: TfIdfRepository = TfIdfRepository(lemmas_tf_idf_repository_name)
	tf_idf: TfIdf = tf_idf_repository.get()

	log.info("Произвожу предрасчёты для векторного поиска")
	alphabet_detector: AlphabetDetector = AlphabetDetector()
	tokenizer: Tokenizer = Tokenizer()
	search: VectorSearch = VectorSearch(tf_idf, TfIdfCalculator())

	while True:
		query: str = input("Введите поисковый запрос: ")
		language = "ru" if "CYRILLIC" in alphabet_detector.detect_alphabet(query) else "en"
		query_lemmas_result: Union[TokenizedDocument, str] = tokenizer.tokenize(query, language, False)
		if not isinstance(query_lemmas_result, TokenizedDocument):
			log.error(f"Не смог распознать запрос {query}. " + query_lemmas_result)
			continue

		query_lemmas: list[str] = [
			lemma
			for lemma, tokens in query_lemmas_result.lemmas.items()
			for _ in tokens]
		result_documents: dict[int, float] = search.search(query_lemmas)

		if len(result_documents) > 0:
			for document_id, reverse_relevance in result_documents.items():
				print(page_urls[document_id], f"({reverse_relevance:.3f})")
		else:
			print("Ничего не найдено")
		print()


if __name__ == '__main__':
	main()
