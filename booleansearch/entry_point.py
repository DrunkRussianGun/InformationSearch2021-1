from re import *
from typing import *

from alphabet_detector import *
from spacy import *

from booleansearch.boolean_search import *
from common.common import *
from common.infrastructure import *
from crawling.raw_document import *
from indexing.inversed_index import *

log = logging.getLogger()


def main():
	configure_logging()

	run()


def run() -> None:
	log.info("Загружаю страницы")
	pages_repository: RawDocumentRepository = RawDocumentRepository(raw_texts_repository_name)
	page_ids = pages_repository.get_all_ids()
	page_urls: dict[int, str] = {
		page_id: pages_repository.get(page_id).url
		for page_id in page_ids}

	log.info("Загружаю инвертированный индекс")
	inversed_index_repository: InversedIndexRepository = InversedIndexRepository(inversed_index_repository_path)
	inversed_index: dict[str, set[int]] = {
		lemma: set(page_ids)
		for lemma, page_ids in inversed_index_repository.get().items()}
	if inversed_index is None:
		log.error("Не смог загрузить инвертированный индекс")
		return

	alphabet_detector: AlphabetDetector = AlphabetDetector()
	operators_regex: Pattern = compile("[&|]")

	while True:
		query: str = input("Введите поисковый запрос: ")
		search: BooleanSearch = BooleanSearch(inversed_index)
		# search создаётся пустым, поэтому комбинируем его с остальным запросом через |
		# Также добавляем в конец фиктивный оператор для обработки последнего операнда
		query = "|" + query + "&"

		operator_matches: Iterator[Match[Union[Union[str, bytes], Any]]] = operators_regex.finditer(query)
		current_match: Match[Union[Union[str, bytes], Any]] = next(operator_matches)
		next_match: Match[Union[Union[str, bytes], Any]]
		for next_match in operator_matches:
			string_between_operators: str = query[current_match.regs[0][1]:next_match.regs[0][0]]\
				.strip()

			operand: str = string_between_operators
			is_operand_negated: bool = operand[0] == "!"
			if is_operand_negated:
				operand = operand[1:]

			operand_lemma: Optional[str] = get_lemma(alphabet_detector, operand)
			if operand_lemma is None:
				continue

			operator: str = query[current_match.regs[0][0]]
			if operator == "&":
				search.and_(operand_lemma, is_operand_negated)
			elif operator == "|":
				search.or_(operand_lemma, is_operand_negated)
			else:
				raise ValueError("Неизвестный оператор: " + operator)

			current_match = next_match

		page_id: int
		if len(search.found_page_ids) > 0:
			for page_id in search.found_page_ids:
				print(page_urls[page_id])
		else:
			print("Ничего не найдено")

		print()


def get_lemma(alphabet_detector: AlphabetDetector, operand: str) -> Optional[str]:
	language_code: str = "ru" if "CYRILLIC" in alphabet_detector.detect_alphabet(operand) else "en"

	language_processor: Optional[Language] = get_language_processor(language_code)
	lemmas: list[str] = [token.lemma_ for token in language_processor(operand)]
	if len(lemmas) != 1:
		log.error(f"Ожидал единственное слово, получил {lemmas}")

	return lemmas[0]


if __name__ == '__main__':
	main()
