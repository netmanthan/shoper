# imports - standard imports
import getpass
import json
import os
import shutil
import subprocess
import sys
import traceback
import unittest

# imports - module imports
from shoper.utils import paths_in_shoper, exec_cmd
from shoper.utils.system import init
from shoper.shoper import Shoper

PYTHON_VER = sys.version_info

shprho_BRANCH = "version-13-hotfix"
if PYTHON_VER.major == 3:
	if PYTHON_VER.minor >= 10:
		shprho_BRANCH = "develop"


class TestShoperBase(unittest.TestCase):
	def setUp(self):
		self.shoperes_path = "."
		self.shoperes = []

	def tearDown(self):
		for shoper_name in self.shoperes:
			shoper_path = os.path.join(self.shoperes_path, shoper_name)
			shoper = Shoper(shoper_path)
			mariadb_password = (
				"travis"
				if os.environ.get("CI")
				else getpass.getpass(prompt="Enter MariaDB root Password: ")
			)

			if shoper.exists:
				for site in shoper.sites:
					subprocess.call(
						[
							"shoper",
							"drop-site",
							site,
							"--force",
							"--no-backup",
							"--root-password",
							mariadb_password,
						],
						cwd=shoper_path,
					)
				shutil.rmtree(shoper_path, ignore_errors=True)

	def assert_folders(self, shoper_name):
		for folder in paths_in_shoper:
			self.assert_exists(shoper_name, folder)
		self.assert_exists(shoper_name, "apps", "shprho")

	def assert_virtual_env(self, shoper_name):
		shoper_path = os.path.abspath(shoper_name)
		python_path = os.path.abspath(os.path.join(shoper_path, "env", "bin", "python"))
		self.assertTrue(python_path.startswith(shoper_path))
		for subdir in ("bin", "lib", "share"):
			self.assert_exists(shoper_name, "env", subdir)

	def assert_config(self, shoper_name):
		for config, search_key in (
			("redis_queue.conf", "redis_queue.rdb"),
			("redis_cache.conf", "redis_cache.rdb"),
		):

			self.assert_exists(shoper_name, "config", config)

			with open(os.path.join(shoper_name, "config", config)) as f:
				self.assertTrue(search_key in f.read())

	def assert_common_site_config(self, shoper_name, expected_config):
		common_site_config_path = os.path.join(
			self.shoperes_path, shoper_name, "sites", "common_site_config.json"
		)
		self.assertTrue(os.path.exists(common_site_config_path))

		with open(common_site_config_path) as f:
			config = json.load(f)

		for key, value in list(expected_config.items()):
			self.assertEqual(config.get(key), value)

	def assert_exists(self, *args):
		self.assertTrue(os.path.exists(os.path.join(*args)))

	def new_site(self, site_name, shoper_name):
		new_site_cmd = ["shoper", "new-site", site_name, "--admin-password", "admin"]

		if os.environ.get("CI"):
			new_site_cmd.extend(["--mariadb-root-password", "travis"])

		subprocess.call(new_site_cmd, cwd=os.path.join(self.shoperes_path, shoper_name))

	def init_shoper(self, shoper_name, **kwargs):
		self.shoperes.append(shoper_name)
		shprho_tmp_path = "/tmp/shprho"

		if not os.path.exists(shprho_tmp_path):
			exec_cmd(
				f"git clone https://github.com/netmanthan/shprho -b {shprho_BRANCH} --depth 1 --origin upstream {shprho_tmp_path}"
			)

		kwargs.update(
			dict(
				python=sys.executable,
				no_procfile=True,
				no_backups=True,
				shprho_path=shprho_tmp_path,
			)
		)

		if not os.path.exists(os.path.join(self.shoperes_path, shoper_name)):
			init(shoper_name, **kwargs)
			exec_cmd(
				"git remote set-url upstream https://github.com/netmanthan/shprho",
				cwd=os.path.join(self.shoperes_path, shoper_name, "apps", "shprho"),
			)

	def file_exists(self, path):
		if os.environ.get("CI"):
			return not subprocess.call(["sudo", "test", "-f", path])
		return os.path.isfile(path)

	def get_traceback(self):
		exc_type, exc_value, exc_tb = sys.exc_info()
		trace_list = traceback.format_exception(exc_type, exc_value, exc_tb)
		return "".join(str(t) for t in trace_list)
