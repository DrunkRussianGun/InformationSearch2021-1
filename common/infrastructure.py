import logging
import os
import traceback

from tinydb import TinyDB

database_file_name = "database.json"
log_file_name = "log"
log_file_encoding = "utf-8"


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


def configure_logging():
	log_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(logging.INFO)
	root_logger.addHandler(console_handler)

	file_handler = logging.FileHandler(log_file_name, encoding = log_file_encoding)
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(logging.DEBUG)
	root_logger.addHandler(file_handler)


def format_exception(exception):
	return os.linesep.join(traceback.format_exception_only(type(exception), exception))


def get_tinydb_table(database_file_path):
	return TinyDB(database_file_path, encoding = "utf-8", ensure_ascii = False, separators = (",", ":"))
