#
from collections import Iterable
from .html_header import *
#
def replace_all(text, dic):
	for i, j in dic.items():
		text = text.replace(i, j)
	return text

def flatten(items):
	"""Yield items from any nested iterable; see Reference."""
	for x in items:
		if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
			for sub_x in flatten(x):
				yield sub_x
		else:
			yield x

def remove_none(obj):
	if isinstance(obj, (list, tuple, set)):
		return type(obj)(remove_none(x) for x in obj if x is not None)
	elif isinstance(obj, dict):
		return type(obj)((remove_none(k), remove_none(v))
			for k, v in obj.items() if k is not None and v is not None)
	else:
		return obj
#
def combine_header(text, title):
	#
	_html = header
	return _html.replace("%%%TITLE%%%", title).replace("%%%CONTENT%%%", text)
	#
