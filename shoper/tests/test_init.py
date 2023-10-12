# imports - standard imports
import json
import os
import subprocess
import unittest

# imports - third paty imports
import git

# imports - module imports
from shoper.utils import exec_cmd
from shoper.app import App
from shoper.tests.test_base import shprho_BRANCH, TestShoperBase
from shoper.shoper import Shoper


# changed from shprho_theme because it wasn't maintained and incompatible,
# chat app & wiki was breaking too. hopefully shprho_docs will be maintained
# for longer since docs.shopersolutions.com is powered by it ;)
TEST_shprho_APP = "shprho_docs"


class TestShoperInit(TestShoperBase):
	def test_utils(self):
		self.assertEqual(subprocess.call("shoper"), 0)

	def test_init(self, shoper_name="test-shoper", **kwargs):
		self.init_shoper(shoper_name, **kwargs)
		app = App("file:///tmp/shprho")
		self.assertTupleEqual(
			(app.mount_path, app.url, app.repo, app.app_name, app.org),
			("/tmp/shprho", "file:///tmp/shprho", "shprho", "shprho", "shprho"),
		)
		self.assert_folders(shoper_name)
		self.assert_virtual_env(shoper_name)
		self.assert_config(shoper_name)
		test_shoper = Shoper(shoper_name)
		app = App("shprho", shoper=test_shoper)
		self.assertEqual(app.from_apps, True)

	def basic(self):
		try:
			self.test_init()
		except Exception:
			print(self.get_traceback())

	def test_multiple_shoperes(self):
		for shoper_name in ("test-shoper-1", "test-shoper-2"):
			self.init_shoper(shoper_name, skip_assets=True)

		self.assert_common_site_config(
			"test-shoper-1",
			{
				"webserver_port": 8000,
				"socketio_port": 9000,
				"file_watcher_port": 6787,
				"redis_queue": "redis://localhost:11000",
				"redis_socketio": "redis://localhost:13000",
				"redis_cache": "redis://localhost:13000",
			},
		)

		self.assert_common_site_config(
			"test-shoper-2",
			{
				"webserver_port": 8001,
				"socketio_port": 9001,
				"file_watcher_port": 6788,
				"redis_queue": "redis://localhost:11001",
				"redis_socketio": "redis://localhost:13001",
				"redis_cache": "redis://localhost:13001",
			},
		)

	def test_new_site(self):
		shoper_name = "test-shoper"
		site_name = "test-site.local"
		shoper_path = os.path.join(self.shoperes_path, shoper_name)
		site_path = os.path.join(shoper_path, "sites", site_name)
		site_config_path = os.path.join(site_path, "site_config.json")

		self.init_shoper(shoper_name)
		self.new_site(site_name, shoper_name)

		self.assertTrue(os.path.exists(site_path))
		self.assertTrue(os.path.exists(os.path.join(site_path, "private", "backups")))
		self.assertTrue(os.path.exists(os.path.join(site_path, "private", "files")))
		self.assertTrue(os.path.exists(os.path.join(site_path, "public", "files")))
		self.assertTrue(os.path.exists(site_config_path))

		with open(site_config_path) as f:
			site_config = json.loads(f.read())

			for key in ("db_name", "db_password"):
				self.assertTrue(key in site_config)
				self.assertTrue(site_config[key])

	def test_get_app(self):
		self.init_shoper("test-shoper", skip_assets=True)
		shoper_path = os.path.join(self.shoperes_path, "test-shoper")
		exec_cmd(f"shoper get-app {TEST_shprho_APP} --skip-assets", cwd=shoper_path)
		self.assertTrue(os.path.exists(os.path.join(shoper_path, "apps", TEST_shprho_APP)))
		app_installed_in_env = TEST_shprho_APP in subprocess.check_output(
			["shoper", "pip", "freeze"], cwd=shoper_path
		).decode("utf8")
		self.assertTrue(app_installed_in_env)

	@unittest.skipIf(shprho_BRANCH != "develop", "only for develop branch")
	def test_get_app_resolve_deps(self):
		shprho_APP = "healthcare"
		self.init_shoper("test-shoper", skip_assets=True)
		shoper_path = os.path.join(self.shoperes_path, "test-shoper")
		exec_cmd(f"shoper get-app {shprho_APP} --resolve-deps --skip-assets", cwd=shoper_path)
		self.assertTrue(os.path.exists(os.path.join(shoper_path, "apps", shprho_APP)))

		states_path = os.path.join(shoper_path, "sites", "apps.json")
		self.assertTrue(os.path.exists(states_path))

		with open(states_path) as f:
			states = json.load(f)

		self.assertTrue(shprho_APP in states)

	def test_install_app(self):
		shoper_name = "test-shoper"
		site_name = "install-app.test"
		shoper_path = os.path.join(self.shoperes_path, "test-shoper")

		self.init_shoper(shoper_name, skip_assets=True)
		exec_cmd(
			f"shoper get-app {TEST_shprho_APP} --branch master --skip-assets", cwd=shoper_path
		)

		self.assertTrue(os.path.exists(os.path.join(shoper_path, "apps", TEST_shprho_APP)))

		# check if app is installed
		app_installed_in_env = TEST_shprho_APP in subprocess.check_output(
			["shoper", "pip", "freeze"], cwd=shoper_path
		).decode("utf8")
		self.assertTrue(app_installed_in_env)

		# create and install app on site
		self.new_site(site_name, shoper_name)
		installed_app = not exec_cmd(
			f"shoper --site {site_name} install-app {TEST_shprho_APP}",
			cwd=shoper_path,
			_raise=False,
		)

		if installed_app:
			app_installed_on_site = subprocess.check_output(
				["shoper", "--site", site_name, "list-apps"], cwd=shoper_path
			).decode("utf8")
			self.assertTrue(TEST_shprho_APP in app_installed_on_site)

	def test_remove_app(self):
		self.init_shoper("test-shoper", skip_assets=True)
		shoper_path = os.path.join(self.shoperes_path, "test-shoper")

		exec_cmd(
			f"shoper get-app {TEST_shprho_APP} --branch master --overwrite --skip-assets",
			cwd=shoper_path,
		)
		exec_cmd(f"shoper remove-app {TEST_shprho_APP}", cwd=shoper_path)

		with open(os.path.join(shoper_path, "sites", "apps.txt")) as f:
			self.assertFalse(TEST_shprho_APP in f.read())
		self.assertFalse(
			TEST_shprho_APP
			in subprocess.check_output(["shoper", "pip", "freeze"], cwd=shoper_path).decode("utf8")
		)
		self.assertFalse(os.path.exists(os.path.join(shoper_path, "apps", TEST_shprho_APP)))

	def test_switch_to_branch(self):
		self.init_shoper("test-shoper", skip_assets=True)
		shoper_path = os.path.join(self.shoperes_path, "test-shoper")
		app_path = os.path.join(shoper_path, "apps", "shprho")

		# * chore: change to 14 when avalible
		prevoius_branch = "version-13"
		if shprho_BRANCH != "develop":
			# assuming we follow `version-#`
			prevoius_branch = f"version-{int(shprho_BRANCH.split('-')[1]) - 1}"

		successful_switch = not exec_cmd(
			f"shoper switch-to-branch {prevoius_branch} shprho --upgrade",
			cwd=shoper_path,
			_raise=False,
		)
		if successful_switch:
			app_branch_after_switch = str(git.Repo(path=app_path).active_branch)
			self.assertEqual(prevoius_branch, app_branch_after_switch)

		successful_switch = not exec_cmd(
			f"shoper switch-to-branch {shprho_BRANCH} shprho --upgrade",
			cwd=shoper_path,
			_raise=False,
		)
		if successful_switch:
			app_branch_after_second_switch = str(git.Repo(path=app_path).active_branch)
			self.assertEqual(shprho_BRANCH, app_branch_after_second_switch)


if __name__ == "__main__":
	unittest.main()
