"""Module for setting up system and respective shoper configurations"""


def env():
	from jinja2 import Environment, PackageLoader

	return Environment(loader=PackageLoader("shoper.config"))
