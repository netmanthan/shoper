VERSION = "5.17.2"
PROJECT_NAME = "shprho-shoper"
shprho_VERSION = None
current_path = None
updated_path = None
LOG_BUFFER = []


def set_shprho_version(shoper_path="."):
	from .utils.app import get_current_shprho_version

	global shprho_VERSION
	if not shprho_VERSION:
		shprho_VERSION = get_current_shprho_version(shoper_path=shoper_path)
