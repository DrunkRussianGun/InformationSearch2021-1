class BooleanSearch:
	inversed_index: dict[str, set[int]]
	all_page_ids: set[int]
	found_page_ids: set[int]

	def __init__(self, inversed_index: dict[str, set[int]]):
		self.inversed_index = inversed_index
		self.all_page_ids = set(
			page_id
			for lemma, page_ids in inversed_index.items()
			for page_id in page_ids)
		self.found_page_ids = set()

	def and_(self, word: str, negated: bool) -> None:
		word_page_ids = self.__get_page_ids(word, negated)
		self.found_page_ids.intersection_update(word_page_ids)

	def or_(self, word: str, negated: bool) -> None:
		word_page_ids = self.__get_page_ids(word, negated)
		self.found_page_ids = self.found_page_ids.union(word_page_ids)

	def __get_page_ids(self, word: str, negated: bool) -> set[int]:
		page_ids = self.inversed_index.get(word, set())
		if negated:
			page_ids = self.all_page_ids.difference(page_ids)
		return page_ids
