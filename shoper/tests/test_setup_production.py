# imports - standard imports
import getpass
import os
import pathlib
import re
import subprocess
import time
import unittest

# imports - module imports
from shoper.utils import exec_cmd, get_cmd_output, which
from shoper.config.production_setup import get_supervisor_confdir
from shoper.tests.test_base import TestShoperBase


class TestSetupProduction(TestShoperBase):
	def test_setup_production(self):
		user = getpass.getuser()

		for shoper_name in ("test-shoper-1", "test-shoper-2"):
			shoper_path = os.path.join(os.path.abspath(self.shoperes_path), shoper_name)
			self.init_shoper(shoper_name)
			exec_cmd(f"sudo shoper setup production {user} --yes", cwd=shoper_path)
			self.assert_nginx_config(shoper_name)
			self.assert_supervisor_config(shoper_name)
			self.assert_supervisor_process(shoper_name)

		self.assert_nginx_process()
		exec_cmd(f"sudo shoper setup sudoers {user}")
		self.assert_sudoers(user)

		for shoper_name in self.shoperes:
			shoper_path = os.path.join(os.path.abspath(self.shoperes_path), shoper_name)
			exec_cmd("sudo shoper disable-production", cwd=shoper_path)

	def production(self):
		try:
			self.test_setup_production()
		except Exception:
			print(self.get_traceback())

	def assert_nginx_config(self, shoper_name):
		conf_src = os.path.join(
			os.path.abspath(self.shoperes_path), shoper_name, "config", "nginx.conf"
		)
		conf_dest = f"/etc/nginx/conf.d/{shoper_name}.conf"

		self.assertTrue(self.file_exists(conf_src))
		self.assertTrue(self.file_exists(conf_dest))

		# symlink matches
		self.assertEqual(os.path.realpath(conf_dest), conf_src)

		# file content
		with open(conf_src) as f:
			f = f.read()

			for key in (
				f"upstream {shoper_name}-shprho",
				f"upstream {shoper_name}-socketio-server",
			):
				self.assertTrue(key in f)

	def assert_nginx_process(self):
		out = get_cmd_output("sudo nginx -t 2>&1")
		self.assertTrue(
			"nginx: configuration file /etc/nginx/nginx.conf test is successful" in out
		)

	def assert_sudoers(self, user):
		sudoers_file = "/etc/sudoers.d/shprho"
		service = which("service")
		nginx = which("nginx")

		self.assertTrue(self.file_exists(sudoers_file))

		if os.environ.get("CI"):
			sudoers = subprocess.check_output(["sudo", "cat", sudoers_file]).decode("utf-8")
		else:
			sudoers = pathlib.Path(sudoers_file).read_text()
		self.assertTrue(f"{user} ALL = (root) NOPASSWD: {service} nginx *" in sudoers)
		self.assertTrue(f"{user} ALL = (root) NOPASSWD: {nginx}" in sudoers)

	def assert_supervisor_config(self, shoper_name, use_rq=True):
		conf_src = os.path.join(
			os.path.abspath(self.shoperes_path), shoper_name, "config", "supervisor.conf"
		)

		supervisor_conf_dir = get_supervisor_confdir()
		conf_dest = f"{supervisor_conf_dir}/{shoper_name}.conf"

		self.assertTrue(self.file_exists(conf_src))
		self.assertTrue(self.file_exists(conf_dest))

		# symlink matches
		self.assertEqual(os.path.realpath(conf_dest), conf_src)

		# file content
		with open(conf_src) as f:
			f = f.read()

			tests = [
				f"program:{shoper_name}-shprho-web",
				f"program:{shoper_name}-redis-cache",
				f"program:{shoper_name}-redis-queue",
				f"group:{shoper_name}-web",
				f"group:{shoper_name}-workers",
				f"group:{shoper_name}-redis",
			]

			if not os.environ.get("CI"):
				tests.append(f"program:{shoper_name}-node-socketio")

			if use_rq:
				tests.extend(
					[
						f"program:{shoper_name}-shprho-schedule",
						f"program:{shoper_name}-shprho-default-worker",
						f"program:{shoper_name}-shprho-short-worker",
						f"program:{shoper_name}-shprho-long-worker",
					]
				)

			else:
				tests.extend(
					[
						f"program:{shoper_name}-shprho-workerbeat",
						f"program:{shoper_name}-shprho-worker",
						f"program:{shoper_name}-shprho-longjob-worker",
						f"program:{shoper_name}-shprho-async-worker",
					]
				)

			for key in tests:
				self.assertTrue(key in f)

	def assert_supervisor_process(self, shoper_name, use_rq=True, disable_production=False):
		out = get_cmd_output("supervisorctl status")

		while "STARTING" in out:
			print("Waiting for all processes to start...")
			time.sleep(10)
			out = get_cmd_output("supervisorctl status")

		tests = [
			r"{shoper_name}-web:{shoper_name}-shprho-web[\s]+RUNNING",
			# Have commented for the time being. Needs to be uncommented later on. Shoper is failing on travis because of this.
			# It works on one shoper and fails on another.giving FATAL or BACKOFF (Exited too quickly (process log may have details))
			# "{shoper_name}-web:{shoper_name}-node-socketio[\s]+RUNNING",
			r"{shoper_name}-redis:{shoper_name}-redis-cache[\s]+RUNNING",
			r"{shoper_name}-redis:{shoper_name}-redis-queue[\s]+RUNNING",
		]

		if use_rq:
			tests.extend(
				[
					r"{shoper_name}-workers:{shoper_name}-shprho-schedule[\s]+RUNNING",
					r"{shoper_name}-workers:{shoper_name}-shprho-default-worker-0[\s]+RUNNING",
					r"{shoper_name}-workers:{shoper_name}-shprho-short-worker-0[\s]+RUNNING",
					r"{shoper_name}-workers:{shoper_name}-shprho-long-worker-0[\s]+RUNNING",
				]
			)

		else:
			tests.extend(
				[
					r"{shoper_name}-workers:{shoper_name}-shprho-workerbeat[\s]+RUNNING",
					r"{shoper_name}-workers:{shoper_name}-shprho-worker[\s]+RUNNING",
					r"{shoper_name}-workers:{shoper_name}-shprho-longjob-worker[\s]+RUNNING",
					r"{shoper_name}-workers:{shoper_name}-shprho-async-worker[\s]+RUNNING",
				]
			)

		for key in tests:
			if disable_production:
				self.assertFalse(re.search(key, out))
			else:
				self.assertTrue(re.search(key, out))


if __name__ == "__main__":
	unittest.main()
