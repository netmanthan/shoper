# imports - standard imports
import getpass
import os
import subprocess

# imports - module imports
from shoper.cli import change_uid_msg
from shoper.config.production_setup import get_supervisor_confdir, is_centos7, service
from shoper.config.common_site_config import get_config
from shoper.utils import exec_cmd, get_shoper_name, get_cmd_output


def is_sudoers_set():
	"""Check if shoper sudoers is set"""
	cmd = ["sudo", "-n", "shoper"]
	shoper_warn = False

	with open(os.devnull, "wb") as f:
		return_code_check = not subprocess.call(cmd, stdout=f)

	if return_code_check:
		try:
			shoper_warn = change_uid_msg in get_cmd_output(cmd, _raise=False)
		except subprocess.CalledProcessError:
			shoper_warn = False
		finally:
			return_code_check = return_code_check and shoper_warn

	return return_code_check


def is_production_set(shoper_path):
	"""Check if production is set for current shoper"""
	production_setup = False
	shoper_name = get_shoper_name(shoper_path)

	supervisor_conf_extn = "ini" if is_centos7() else "conf"
	supervisor_conf_file_name = f"{shoper_name}.{supervisor_conf_extn}"
	supervisor_conf = os.path.join(get_supervisor_confdir(), supervisor_conf_file_name)

	if os.path.exists(supervisor_conf):
		production_setup = production_setup or True

	nginx_conf = f"/etc/nginx/conf.d/{shoper_name}.conf"

	if os.path.exists(nginx_conf):
		production_setup = production_setup or True

	return production_setup


def execute(shoper_path):
	"""This patch checks if shoper sudoers is set and regenerate supervisor and sudoers files"""
	user = get_config(".").get("shprho_user") or getpass.getuser()

	if is_sudoers_set():
		if is_production_set(shoper_path):
			exec_cmd(f"sudo shoper setup supervisor --yes --user {user}")
			service("supervisord", "restart")

		exec_cmd(f"sudo shoper setup sudoers {user}")
