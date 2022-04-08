import re
import string
from typing import Optional, Type, Union

import en_core_web_md
import ru_core_news_md
import spacy
from spacy import Language
from spacy.tokens import Token
from spacy_langdetect import LanguageDetector


class TokenizedDocument:
	def __init__(self, language: str):
		self.language: str = language
		self.tokens: list[str] = []
		self.lemmas: dict[str, list[str]] = {}


class Tokenizer:
	available_language_codes = {"en", "ru"}

	__punctuation_whitespacing_map: dict[int, str] = {
		ord(symbol): " "
		for symbol in string.punctuation + string.whitespace + "«»—–“”•☆№\""}

	def __init__(self):
		self.__language_detector = self.__create_language_detector()
		self.__language_processors_cache: dict[str, Language] = {}

	def tokenize(
			self,
			text: str,
			language: Optional[str] = None,
			remove_tokens_with_stop_words: bool = True) -> Union[TokenizedDocument, str]:
		text = self.__preprocess_text(text)

		if language is None:
			language = self.__language_detector(text)._.language.get("language")
			if language is None:
				return "Не смог определить язык"

		language_processor: Optional[Language] = self.__create_language_processor(language)
		if language_processor is None:
			return "Не нашёл обработчик языка " + language

		processed_text: list[Type[Token]] = [
			token
			for token in language_processor(text)
			if token.is_alpha]

		document = TokenizedDocument(language)

		document.tokens = (
			token.text
			for token in (
				processed_text
				if not remove_tokens_with_stop_words
				else filter(lambda x: not x.is_stop, processed_text)))

		document.lemmas = {}
		for token in processed_text:
			document.lemmas.setdefault(token.lemma_, []).append(token.text)
		return document

	def __create_language_processor(self, language: str, **load_kwargs):
		processor = self.__language_processors_cache.get(language)
		if processor is not None:
			return processor

		if language not in self.available_language_codes:
			return None
		if language == "en":
			processor = en_core_web_md.load(**load_kwargs)
		elif language == "ru":
			processor = ru_core_news_md.load(**load_kwargs)
		else:
			processor = None

		self.__language_processors_cache[language] = processor
		return processor

	@staticmethod
	def __create_language_detector():
		@Language.factory("language_detector")
		def create_language_detector(nlp, name):
			return LanguageDetector()

		language_detector = spacy.blank("en")
		language_detector.add_pipe("sentencizer")
		language_detector.add_pipe("language_detector")
		return language_detector

	@staticmethod
	def __preprocess_text(text: str):
		# Убираем URL
		text = re.sub("((https?|ftp)://|(www|ftp)\\.)?[a-z0-9-]+(\\.[a-z0-9-]+)+([/?].*)?", " ", text)
		# Меняем знаки пунктуации на пробелы
		text = text.translate(Tokenizer.__punctuation_whitespacing_map)

		return text
