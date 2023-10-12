class InvalidBranchException(Exception):
	pass


class InvalidRemoteException(Exception):
	pass


class PatchError(Exception):
	pass


class CommandFailedError(Exception):
	pass


class ShoperNotFoundError(Exception):
	pass


class ValidationError(Exception):
	pass


class AppNotInstalledError(ValidationError):
	pass


class CannotUpdateReleaseShoper(ValidationError):
	pass


class FeatureDoesNotExistError(CommandFailedError):
	pass


class NotInShoperDirectoryError(Exception):
	pass


class VersionNotFound(Exception):
	pass
