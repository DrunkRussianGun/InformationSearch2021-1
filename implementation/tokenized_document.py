from pathlib import Path

from tinydb import table

from implementation.infrastructure import get_tinydb_table

tokenized_texts_repository_name = "tokenized_texts"


class TokenizedDocument:
	def __init__(self, id_, url, language_code, tokens, lemmas):
		self.id_ = id_
		self.url = url
		self.language_code = language_code
		self.tokens = tokens
		self.lemmas = lemmas


class TokenizedDocumentRepository:
	__file_encoding = "utf-8"
	__token_separator = "\n"
	__lemma_line_separator = "\n"
	__lemma_separator = ":\t"
	__lemma_tokens_separator = "\t"

	def __init__(self, name = ""):
		name = name if len(name) > 0 else "default"
		repository_path = Path(name)
		self.__documents_path = repository_path.joinpath("documents")

		self.__documents_path.joinpath("tokens").mkdir(parents = True, exist_ok = True)
		self.__documents_path.joinpath("lemmas").mkdir(parents = True, exist_ok = True)
		self.__table = get_tinydb_table(repository_path.joinpath("index.json"))
		self.__check_and_correct_table()

	def get_all_ids(self):
		return [document.doc_id for document in self.__table.all()]

	def get(self, id_):
		document_properties = self.__table.get(doc_id = id_)
		if document_properties is None:
			return None

		document = object.__new__(TokenizedDocument)
		vars(document).update(document_properties)
		document.id_ = id_

		with open(
				self.__get_token_full_file_name(id_),
				"r",
				encoding = TokenizedDocumentRepository.__file_encoding) as file:
			document.tokens = file.read().split(TokenizedDocumentRepository.__token_separator)

		with open(
				self.__get_lemma_full_file_name(id_),
				"r",
				encoding = TokenizedDocumentRepository.__file_encoding) as file:
			document.lemmas = {}
			lemma_lines = file.read().split(TokenizedDocumentRepository.__lemma_line_separator)
			for lemma_line in lemma_lines:
				lemma, lemma_tokens_line = lemma_line.split(TokenizedDocumentRepository.__lemma_separator)
				lemma_tokens = lemma_tokens_line.split(TokenizedDocumentRepository.__lemma_tokens_separator)
				document.lemmas[lemma] = lemma_tokens

		return document

	def create(self, document):
		if self.__table.contains(doc_id = document.id_):
			raise RuntimeError(
				f"Не смог создать документ с номером {document.id_} в хранилище, "
				+ f"т. к. документ с таким номером уже существует")

		document_properties = dict(vars(document))
		document_properties.pop("id_")
		document_properties.pop("tokens")
		self.__table.insert(table.Document(document_properties, doc_id = document.id_))

		with open(
				self.__get_token_full_file_name(document.id_),
				"w",
				encoding = TokenizedDocumentRepository.__file_encoding) as file:
			file.write(TokenizedDocumentRepository.__token_separator.join(document.tokens))
		with open(
				self.__get_lemma_full_file_name(document.id_),
				"w",
				encoding = TokenizedDocumentRepository.__file_encoding) as file:
			file.write(
				TokenizedDocumentRepository.__lemma_line_separator.join(
					f"{lemma}{self.__lemma_separator}"
					+ self.__lemma_tokens_separator.join(tokens)
					for lemma, tokens in document.lemmas.items()))

	def delete_all(self):
		for document in self.__table.all():
			Path(self.__get_token_full_file_name(document.doc_id)).unlink(True)
			Path(self.__get_lemma_full_file_name(document.doc_id)).unlink(True)

		self.__table.truncate()

	def __get_token_full_file_name(self, id_):
		return self.__documents_path.joinpath(f"tokens/tokens_{id_}.txt")

	def __get_lemma_full_file_name(self, id_):
		return self.__documents_path.joinpath(f"lemmas/lemmas_{id_}.txt")

	def __check_and_correct_table(self):
		for id_ in self.get_all_ids():
			if not Path(self.__get_token_full_file_name(id_)).is_file():
				self.__table.remove(doc_ids = [id_])
				continue
			if not Path(self.__get_lemma_full_file_name(id_)).is_file():
				self.__table.remove(doc_ids = [id_])
