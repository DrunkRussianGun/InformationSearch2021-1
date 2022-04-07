from shutil import *
from pathlib import *

from tfidf.tf_idf import *

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
						f"{tf_idf.idf[word]:.6f}{TfIdfRepository.__field_separator}"
						f"{tf_idf_value:.6f}"
						for word, tf_idf_value in document_tf_idf.items()))

	def delete_all(self):
		rmtree(self.__documents_path, True)
		self.__documents_path.mkdir()

	def __get_document_full_file_name(self, document_id: int):
		return self.__documents_path.joinpath(f"{document_id}.txt")
