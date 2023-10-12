import os
import shutil
import subprocess
import unittest

from shoper.app import App
from shoper.shoper import Shoper
from shoper.exceptions import InvalidRemoteException
from shoper.utils import is_valid_shprho_branch


class TestUtils(unittest.TestCase):
	def test_app_utils(self):
		git_url = "https://github.com/netmanthan/shprho"
		branch = "develop"
		app = App(name=git_url, branch=branch, shoper=Shoper("."))
		self.assertTrue(
			all(
				[
					app.name == git_url,
					app.branch == branch,
					app.tag == branch,
					app.is_url is True,
					app.on_disk is False,
					app.org == "shprho",
					app.url == git_url,
				]
			)
		)

	def test_is_valid_shprho_branch(self):
		with self.assertRaises(InvalidRemoteException):
			is_valid_shprho_branch(
				"https://github.com/netmanthan/shprho.git", shprho_branch="random-branch"
			)
			is_valid_shprho_branch(
				"https://github.com/random/random.git", shprho_branch="random-branch"
			)

		is_valid_shprho_branch(
			"https://github.com/netmanthan/shprho.git", shprho_branch="develop"
		)
		is_valid_shprho_branch(
			"https://github.com/netmanthan/shprho.git", shprho_branch="v13.29.0"
		)

	def test_app_states(self):
		shoper_dir = "./sandbox"
		sites_dir = os.path.join(shoper_dir, "sites")

		if not os.path.exists(sites_dir):
			os.makedirs(sites_dir)

		fake_shoper = Shoper(shoper_dir)

		self.assertTrue(hasattr(fake_shoper.apps, "states"))

		fake_shoper.apps.states = {
			"shprho": {
				"resolution": {"branch": "develop", "commit_hash": "234rwefd"},
				"version": "14.0.0-dev",
			}
		}
		fake_shoper.apps.update_apps_states()

		self.assertEqual(fake_shoper.apps.states, {})

		shprho_path = os.path.join(shoper_dir, "apps", "shprho")

		os.makedirs(os.path.join(shprho_path, "shprho"))

		subprocess.run(["git", "init"], cwd=shprho_path, capture_output=True, check=True)

		with open(os.path.join(shprho_path, "shprho", "__init__.py"), "w+") as f:
			f.write("__version__ = '11.0'")

		subprocess.run(["git", "add", "."], cwd=shprho_path, capture_output=True, check=True)
		subprocess.run(
			["git", "config", "user.email", "shoper-test_app_states@gha.com"],
			cwd=shprho_path,
			capture_output=True,
			check=True,
		)
		subprocess.run(
			["git", "config", "user.name", "App States Test"],
			cwd=shprho_path,
			capture_output=True,
			check=True,
		)
		subprocess.run(
			["git", "commit", "-m", "temp"], cwd=shprho_path, capture_output=True, check=True
		)

		fake_shoper.apps.update_apps_states(app_name="shprho")

		self.assertIn("shprho", fake_shoper.apps.states)
		self.assertIn("version", fake_shoper.apps.states["shprho"])
		self.assertEqual("11.0", fake_shoper.apps.states["shprho"]["version"])

		shutil.rmtree(shoper_dir)

	def test_ssh_ports(self):
		app = App("git@github.com:22:netmanthan/shprho")
		self.assertEqual(
			(app.use_ssh, app.org, app.repo, app.app_name), (True, "shprho", "shprho", "shprho")
		)
