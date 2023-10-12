# imports - standard imports
import getpass
import os

# imports - third partyimports
import click

# imports - module imports
import shoper
from shoper.app import use_rq
from shoper.shoper import Shoper
from shoper.config.common_site_config import (
	get_gunicorn_workers,
	update_config,
	get_default_max_requests,
	compute_max_requests_jitter,
)
from shoper.utils import exec_cmd, which, get_shoper_name


def generate_systemd_config(
	shoper_path,
	user=None,
	yes=False,
	stop=False,
	create_symlinks=False,
	delete_symlinks=False,
):

	if not user:
		user = getpass.getuser()

	config = Shoper(shoper_path).conf

	shoper_dir = os.path.abspath(shoper_path)
	shoper_name = get_shoper_name(shoper_path)

	if stop:
		exec_cmd(
			f"sudo systemctl stop -- $(systemctl show -p Requires {shoper_name}.target | cut -d= -f2)"
		)
		return

	if create_symlinks:
		_create_symlinks(shoper_path)
		return

	if delete_symlinks:
		_delete_symlinks(shoper_path)
		return

	number_of_workers = config.get("background_workers") or 1
	background_workers = []
	for i in range(number_of_workers):
		background_workers.append(
			get_shoper_name(shoper_path) + "-shprho-default-worker@" + str(i + 1) + ".service"
		)

	for i in range(number_of_workers):
		background_workers.append(
			get_shoper_name(shoper_path) + "-shprho-short-worker@" + str(i + 1) + ".service"
		)

	for i in range(number_of_workers):
		background_workers.append(
			get_shoper_name(shoper_path) + "-shprho-long-worker@" + str(i + 1) + ".service"
		)

	web_worker_count = config.get(
		"gunicorn_workers", get_gunicorn_workers()["gunicorn_workers"]
	)
	max_requests = config.get(
		"gunicorn_max_requests", get_default_max_requests(web_worker_count)
	)

	shoper_info = {
		"shoper_dir": shoper_dir,
		"sites_dir": os.path.join(shoper_dir, "sites"),
		"user": user,
		"use_rq": use_rq(shoper_path),
		"http_timeout": config.get("http_timeout", 120),
		"redis_server": which("redis-server"),
		"node": which("node") or which("nodejs"),
		"redis_cache_config": os.path.join(shoper_dir, "config", "redis_cache.conf"),
		"redis_queue_config": os.path.join(shoper_dir, "config", "redis_queue.conf"),
		"webserver_port": config.get("webserver_port", 8000),
		"gunicorn_workers": web_worker_count,
		"gunicorn_max_requests": max_requests,
		"gunicorn_max_requests_jitter": compute_max_requests_jitter(max_requests),
		"shoper_name": get_shoper_name(shoper_path),
		"worker_target_wants": " ".join(background_workers),
		"shoper_cmd": which("shoper"),
	}

	if not yes:
		click.confirm(
			"current systemd configuration will be overwritten. Do you want to continue?",
			abort=True,
		)

	setup_systemd_directory(shoper_path)
	setup_main_config(shoper_info, shoper_path)
	setup_workers_config(shoper_info, shoper_path)
	setup_web_config(shoper_info, shoper_path)
	setup_redis_config(shoper_info, shoper_path)

	update_config({"restart_systemd_on_update": False}, shoper_path=shoper_path)
	update_config({"restart_supervisor_on_update": False}, shoper_path=shoper_path)


def setup_systemd_directory(shoper_path):
	if not os.path.exists(os.path.join(shoper_path, "config", "systemd")):
		os.makedirs(os.path.join(shoper_path, "config", "systemd"))


def setup_main_config(shoper_info, shoper_path):
	# Main config
	shoper_template = shoper.config.env().get_template("systemd/shprho-shoper.target")
	shoper_config = shoper_template.render(**shoper_info)
	shoper_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + ".target"
	)

	with open(shoper_config_path, "w") as f:
		f.write(shoper_config)


def setup_workers_config(shoper_info, shoper_path):
	# Worker Group
	shoper_workers_target_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-workers.target"
	)
	shoper_default_worker_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-shprho-default-worker.service"
	)
	shoper_short_worker_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-shprho-short-worker.service"
	)
	shoper_long_worker_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-shprho-long-worker.service"
	)
	shoper_schedule_worker_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-shprho-schedule.service"
	)

	shoper_workers_target_config = shoper_workers_target_template.render(**shoper_info)
	shoper_default_worker_config = shoper_default_worker_template.render(**shoper_info)
	shoper_short_worker_config = shoper_short_worker_template.render(**shoper_info)
	shoper_long_worker_config = shoper_long_worker_template.render(**shoper_info)
	shoper_schedule_worker_config = shoper_schedule_worker_template.render(**shoper_info)

	shoper_workers_target_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + "-workers.target"
	)
	shoper_default_worker_config_path = os.path.join(
		shoper_path,
		"config",
		"systemd",
		shoper_info.get("shoper_name") + "-shprho-default-worker@.service",
	)
	shoper_short_worker_config_path = os.path.join(
		shoper_path,
		"config",
		"systemd",
		shoper_info.get("shoper_name") + "-shprho-short-worker@.service",
	)
	shoper_long_worker_config_path = os.path.join(
		shoper_path,
		"config",
		"systemd",
		shoper_info.get("shoper_name") + "-shprho-long-worker@.service",
	)
	shoper_schedule_worker_config_path = os.path.join(
		shoper_path,
		"config",
		"systemd",
		shoper_info.get("shoper_name") + "-shprho-schedule.service",
	)

	with open(shoper_workers_target_config_path, "w") as f:
		f.write(shoper_workers_target_config)

	with open(shoper_default_worker_config_path, "w") as f:
		f.write(shoper_default_worker_config)

	with open(shoper_short_worker_config_path, "w") as f:
		f.write(shoper_short_worker_config)

	with open(shoper_long_worker_config_path, "w") as f:
		f.write(shoper_long_worker_config)

	with open(shoper_schedule_worker_config_path, "w") as f:
		f.write(shoper_schedule_worker_config)


def setup_web_config(shoper_info, shoper_path):
	# Web Group
	shoper_web_target_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-web.target"
	)
	shoper_web_service_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-shprho-web.service"
	)
	shoper_node_socketio_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-node-socketio.service"
	)

	shoper_web_target_config = shoper_web_target_template.render(**shoper_info)
	shoper_web_service_config = shoper_web_service_template.render(**shoper_info)
	shoper_node_socketio_config = shoper_node_socketio_template.render(**shoper_info)

	shoper_web_target_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + "-web.target"
	)
	shoper_web_service_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + "-shprho-web.service"
	)
	shoper_node_socketio_config_path = os.path.join(
		shoper_path,
		"config",
		"systemd",
		shoper_info.get("shoper_name") + "-node-socketio.service",
	)

	with open(shoper_web_target_config_path, "w") as f:
		f.write(shoper_web_target_config)

	with open(shoper_web_service_config_path, "w") as f:
		f.write(shoper_web_service_config)

	with open(shoper_node_socketio_config_path, "w") as f:
		f.write(shoper_node_socketio_config)


def setup_redis_config(shoper_info, shoper_path):
	# Redis Group
	shoper_redis_target_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-redis.target"
	)
	shoper_redis_cache_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-redis-cache.service"
	)
	shoper_redis_queue_template = shoper.config.env().get_template(
		"systemd/shprho-shoper-redis-queue.service"
	)

	shoper_redis_target_config = shoper_redis_target_template.render(**shoper_info)
	shoper_redis_cache_config = shoper_redis_cache_template.render(**shoper_info)
	shoper_redis_queue_config = shoper_redis_queue_template.render(**shoper_info)

	shoper_redis_target_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + "-redis.target"
	)
	shoper_redis_cache_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + "-redis-cache.service"
	)
	shoper_redis_queue_config_path = os.path.join(
		shoper_path, "config", "systemd", shoper_info.get("shoper_name") + "-redis-queue.service"
	)

	with open(shoper_redis_target_config_path, "w") as f:
		f.write(shoper_redis_target_config)

	with open(shoper_redis_cache_config_path, "w") as f:
		f.write(shoper_redis_cache_config)

	with open(shoper_redis_queue_config_path, "w") as f:
		f.write(shoper_redis_queue_config)


def _create_symlinks(shoper_path):
	shoper_dir = os.path.abspath(shoper_path)
	etc_systemd_system = os.path.join("/", "etc", "systemd", "system")
	config_path = os.path.join(shoper_dir, "config", "systemd")
	unit_files = get_unit_files(shoper_dir)
	for unit_file in unit_files:
		filename = "".join(unit_file)
		exec_cmd(
			f'sudo ln -s {config_path}/{filename} {etc_systemd_system}/{"".join(unit_file)}'
		)
	exec_cmd("sudo systemctl daemon-reload")


def _delete_symlinks(shoper_path):
	shoper_dir = os.path.abspath(shoper_path)
	etc_systemd_system = os.path.join("/", "etc", "systemd", "system")
	unit_files = get_unit_files(shoper_dir)
	for unit_file in unit_files:
		exec_cmd(f'sudo rm {etc_systemd_system}/{"".join(unit_file)}')
	exec_cmd("sudo systemctl daemon-reload")


def get_unit_files(shoper_path):
	shoper_name = get_shoper_name(shoper_path)
	unit_files = [
		[shoper_name, ".target"],
		[shoper_name + "-workers", ".target"],
		[shoper_name + "-web", ".target"],
		[shoper_name + "-redis", ".target"],
		[shoper_name + "-shprho-default-worker@", ".service"],
		[shoper_name + "-shprho-short-worker@", ".service"],
		[shoper_name + "-shprho-long-worker@", ".service"],
		[shoper_name + "-shprho-schedule", ".service"],
		[shoper_name + "-shprho-web", ".service"],
		[shoper_name + "-node-socketio", ".service"],
		[shoper_name + "-redis-cache", ".service"],
		[shoper_name + "-redis-queue", ".service"],
	]
	return unit_files
