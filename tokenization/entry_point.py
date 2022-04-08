import logging
import os
from typing import Optional, Union

from common.infrastructure import configure_logging, format_exception
from crawling.raw_document import RawDocument, RawDocumentRepository, raw_texts_repository_name
from tokenization.tokenized_page import TokenizedPage, TokenizedPageRepository, \
	tokenized_pages_repository_name
from tokenization.tokenizer import TokenizedDocument, Tokenizer

log = logging.getLogger()


def main():
	configure_logging()

	run()


def run():
	log.info("Инициализирую хранилище страниц")
	pages: RawDocumentRepository = RawDocumentRepository(raw_texts_repository_name)
	page_ids = pages.get_all_ids()

	log.info("Инициализирую хранилище токенизированных текстов")
	tokenized_pages_repository: TokenizedPageRepository = TokenizedPageRepository(tokenized_pages_repository_name)
	tokenized_pages_repository.delete_all()

	tokenizer: Tokenizer = Tokenizer()
	for id_ in page_ids:
		page: Optional[RawDocument] = pages.get(id_)
		tokenized_document_result: Union[TokenizedDocument, str] = tokenizer.tokenize(page.text)
		if not isinstance(tokenized_document_result, TokenizedDocument):
			log.warning(f"Не смог проанализировать страницу {page.url}. " + tokenized_document_result)
			continue

		log.info(f"Язык страницы {page.url}: {tokenized_document_result.language}")
		tokenized_page: TokenizedPage = TokenizedPage(
			id_,
			page.url,
			tokenized_document_result.language,
			tokenized_document_result.tokens,
			tokenized_document_result.lemmas)

		try:
			tokenized_pages_repository.create(tokenized_page)
		except Exception as exception:
			log.error(
				f"Не смог сохранить токенизированный текст страницы {page.url}:" + os.linesep
				+ format_exception(exception))


if __name__ == '__main__':
	main()
