import logging
import os

from common.infrastructure import configure_logging, format_exception
from indexing.inversed_index import InversedIndexRepository, inversed_index_repository_path
from tokenization.tokenized_page import TokenizedPageRepository, tokenized_pages_repository_name

log = logging.getLogger()


def main():
	configure_logging()

	run()


def run():
	log.info("Инициализирую хранилище токенизированных текстов")
	tokenized_pages_repository = TokenizedPageRepository(tokenized_pages_repository_name)

	log.info("Инициализирую хранилище инвертированного индекса")
	inverted_index_repository = InversedIndexRepository(inversed_index_repository_path)

	index = {}
	for document_id in tokenized_pages_repository.get_all_ids():
		tokenized_document = tokenized_pages_repository.get(document_id)
		log.info(f"Обрабатываю страницу {tokenized_document.url} ({len(tokenized_document.lemmas)} токенов)")

		for lemma, _ in tokenized_document.lemmas.items():
			documents_with_lemma = index.setdefault(lemma, [])
			if len(documents_with_lemma) == 0 or documents_with_lemma[-1] != document_id:
				documents_with_lemma.append(document_id)

	log.info("Сохраняю построенный инвертированный индекс")
	try:
		inverted_index_repository.save(index)
	except Exception as exception:
		log.error("Не смог сохранить построенный индекс:" + os.linesep + format_exception(exception))
		raise


if __name__ == '__main__':
	main()
