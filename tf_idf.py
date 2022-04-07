from implementation.infrastructure import *
from implementation.tokenized_document import *
from tfidf.tf_idf import *

log = logging.getLogger()


def main():
	configure_logging()

	run()


def run():
	log.info("Загружаю токенизированные тексты")
	tokenized_texts_repository: TokenizedDocumentRepository = TokenizedDocumentRepository(
		tokenized_texts_repository_name)
	document_ids: list[int] = tokenized_texts_repository.get_all_ids()
	documents: dict[int, TokenizedDocument] = {
		document_id: tokenized_texts_repository.get(document_id)
		for document_id in document_ids}

	tf_idf_calculator = TfIdfCalculator()

	log.info("Рассчитываю TF–IDF токенов")
	document_id_to_token_count_map: dict[int, dict[str, int]] = {
		document_id: count_duplicates(documents[document_id].tokens)
		for document_id in document_ids}
	tokens_tf_idf: TfIdf = tf_idf_calculator.calculate(
		TermsStatistics(document_id_to_token_count_map))

	log.info("Рассчитываю TF–IDF лемм")
	document_id_to_lemma_count_map: dict[int, dict[str, int]] = {
		document_id: {
			lemma: len(tokens)
			for lemma, tokens in documents[document_id].lemmas.items()}
		for document_id in document_ids}
	lemmas_tf_idf: TfIdf = tf_idf_calculator.calculate(
		TermsStatistics(document_id_to_lemma_count_map))


def count_duplicates(elements: list[str]) -> dict[str, int]:
	counts: dict[str, int] = {}
	for element in elements:
		counts.setdefault(element, 0)
		counts[element] += 1
	return counts


if __name__ == '__main__':
	main()
