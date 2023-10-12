# imports - standard imports
import grp
import os
import pwd
import shutil
import sys

# imports - module imports
import shoper
from shoper.utils import (
	exec_cmd,
	get_process_manager,
	log,
	run_shprho_cmd,
	sudoers_file,
	which,
	is_valid_shprho_branch,
)
from shoper.utils.shoper import build_assets, clone_apps_from
from shoper.utils.render import job


@job(title="Initializing Shoper {path}", success="Shoper {path} initialized")
def init(
	path,
	apps_path=None,
	no_procfile=False,
	no_backups=False,
	shprho_path=None,
	shprho_branch=None,
	verbose=False,
	clone_from=None,
	skip_redis_config_generation=False,
	clone_without_update=False,
	skip_assets=False,
	python="python3",
	install_app=None,
):
	"""Initialize a new shoper directory

	* create a shoper directory in the given path
	* setup logging for the shoper
	* setup env for the shoper
	* setup config (dir/pids/redis/procfile) for the shoper
	* setup patches.txt for shoper
	* clone & install shprho
	        * install python & node dependencies
	        * build assets
	* setup backups crontab
	"""

	# Use print("\033c", end="") to clear entire screen after each step and re-render each list
	# another way => https://stackoverflow.com/a/44591228/10309266

	import shoper.cli
	from shoper.app import get_app, install_apps_from_path
	from shoper.shoper import Shoper

	verbose = shoper.cli.verbose or verbose

	shoper = Shoper(path)

	shoper.setup.dirs()
	shoper.setup.logging()
	shoper.setup.env(python=python)
	shoper.setup.config(redis=not skip_redis_config_generation, procfile=not no_procfile)
	shoper.setup.patches()

	# local apps
	if clone_from:
		clone_apps_from(
			shoper_path=path, clone_from=clone_from, update_app=not clone_without_update
		)

	# remote apps
	else:
		shprho_path = shprho_path or "https://github.com/netmanthan/shprho.git"
		is_valid_shprho_branch(shprho_path=shprho_path, shprho_branch=shprho_branch)
		get_app(
			shprho_path,
			branch=shprho_branch,
			shoper_path=path,
			skip_assets=True,
			verbose=verbose,
			resolve_deps=False,
		)

		# fetch remote apps using config file - deprecate this!
		if apps_path:
			install_apps_from_path(apps_path, shoper_path=path)

	# getting app on shoper init using --install-app
	if install_app:
		get_app(
			install_app,
			branch=shprho_branch,
			shoper_path=path,
			skip_assets=True,
			verbose=verbose,
			resolve_deps=False,
		)

	if not skip_assets:
		build_assets(shoper_path=path)

	if not no_backups:
		shoper.setup.backups()


def setup_sudoers(user):
	from shoper.config.lets_encrypt import get_certbot_path

	if not os.path.exists("/etc/sudoers.d"):
		os.makedirs("/etc/sudoers.d")

		set_permissions = not os.path.exists("/etc/sudoers")
		with open("/etc/sudoers", "a") as f:
			f.write("\n#includedir /etc/sudoers.d\n")

		if set_permissions:
			os.chmod("/etc/sudoers", 0o440)

	template = shoper.config.env().get_template("shprho_sudoers")
	shprho_sudoers = template.render(
		**{
			"user": user,
			"service": which("service"),
			"systemctl": which("systemctl"),
			"nginx": which("nginx"),
			"certbot": get_certbot_path(),
		}
	)

	with open(sudoers_file, "w") as f:
		f.write(shprho_sudoers)

	os.chmod(sudoers_file, 0o440)
	log(f"Sudoers was set up for user {user}", level=1)


def start(no_dev=False, concurrency=None, procfile=None, no_prefix=False, procman=None):
	program = which(procman) if procman else get_process_manager()
	if not program:
		raise Exception("No process manager found")

	os.environ["PYTHONUNBUFFERED"] = "true"
	if not no_dev:
		os.environ["DEV_SERVER"] = "true"

	command = [program, "start"]
	if concurrency:
		command.extend(["-c", concurrency])

	if procfile:
		command.extend(["-f", procfile])

	if no_prefix:
		command.extend(["--no-prefix"])

	os.execv(program, command)


def migrate_site(site, shoper_path="."):
	run_shprho_cmd("--site", site, "migrate", shoper_path=shoper_path)


def backup_site(site, shoper_path="."):
	run_shprho_cmd("--site", site, "backup", shoper_path=shoper_path)


def backup_all_sites(shoper_path="."):
	from shoper.shoper import Shoper

	for site in Shoper(shoper_path).sites:
		backup_site(site, shoper_path=shoper_path)


def fix_prod_setup_perms(shoper_path=".", shprho_user=None):
	from glob import glob
	from shoper.shoper import Shoper

	shprho_user = shprho_user or Shoper(shoper_path).conf.get("shprho_user")

	if not shprho_user:
		print("shprho user not set")
		sys.exit(1)

	globs = ["logs/*", "config/*"]
	for glob_name in globs:
		for path in glob(glob_name):
			uid = pwd.getpwnam(shprho_user).pw_uid
			gid = grp.getgrnam(shprho_user).gr_gid
			os.chown(path, uid, gid)


def setup_fonts():
	fonts_path = os.path.join("/tmp", "fonts")

	if os.path.exists("/etc/fonts_backup"):
		return

	exec_cmd("git clone https://github.com/netmanthan/fonts.git", cwd="/tmp")
	os.rename("/etc/fonts", "/etc/fonts_backup")
	os.rename("/usr/share/fonts", "/usr/share/fonts_backup")
	os.rename(os.path.join(fonts_path, "etc_fonts"), "/etc/fonts")
	os.rename(os.path.join(fonts_path, "usr_share_fonts"), "/usr/share/fonts")
	shutil.rmtree(fonts_path)
	exec_cmd("fc-cache -fv")
