from os import walk
from pathlib import Path
from shutil import rmtree

from tfidf.tf_idf import TfIdf

tokens_tf_idf_repository_name: str = "tf-idf/tokens"
lemmas_tf_idf_repository_name: str = "tf-idf/lemmas"


class TfIdfRepository:
	__file_encoding: str = "utf-8"
	__field_separator: str = "\t"
	__tf_idf_separator: str = "\n"

	def __init__(self, name: str = ""):
		name: str = name if len(name) > 0 else "default"
		repository_path: Path = Path(name)
		self.__documents_path = repository_path
		self.__documents_path.mkdir(parents = True, exist_ok = True)

	def create(self, tf_idf: TfIdf):
		if len(tf_idf.tf_idf) <= 0:
			return

		if Path.is_file(self.__get_document_full_file_name(next(iter(tf_idf.tf_idf)))):
			raise RuntimeError(f"Не смог создать файлы для сохранения TF–IDF, т. к. они уже существуют")

		document_id: int
		document_tf_idf: dict[str, float]
		for document_id, document_tf_idf in tf_idf.tf_idf.items():
			with open(
					self.__get_document_full_file_name(document_id),
					"w",
					encoding = TfIdfRepository.__file_encoding) as file:
				file.write(
					TfIdfRepository.__tf_idf_separator.join(
						f"{word}{TfIdfRepository.__field_separator}"
						f"{tf_idf.idf[word]:.12f}{TfIdfRepository.__field_separator}"
						f"{tf_idf_value:.12f}"
						for word, tf_idf_value in document_tf_idf.items()))

	def get(self) -> TfIdf:
		idf: dict[str, float] = {}
		tf_idf: dict[int, dict[str, float]] = {}

		for file_name in next(walk(self.__documents_path), (None, None, []))[2]:
			document_id: int = self.__get_document_id(file_name)
			document_tf_idf: dict[str, float] = {}
			tf_idf[document_id] = document_tf_idf

			with open(
					self.__get_document_full_file_name(document_id),
					"r",
					encoding = TfIdfRepository.__file_encoding) as file:
				tf_idf_lines: list[str] = file.read().split(TfIdfRepository.__tf_idf_separator)
				for tf_idf_line in tf_idf_lines:
					word, idf_value, tf_idf_value = tf_idf_line.split(TfIdfRepository.__field_separator)
					idf.setdefault(word, float(idf_value))
					document_tf_idf[word] = float(tf_idf_value)

		return TfIdf(idf, tf_idf)

	def delete_all(self):
		rmtree(self.__documents_path, True)
		self.__documents_path.mkdir()

	def __get_document_full_file_name(self, document_id: int):
		return self.__documents_path.joinpath(f"{document_id}.txt")

	def __get_document_id(self, document_file_name: str) -> int:
		return int(document_file_name[:len(document_file_name) - len(".txt")])
