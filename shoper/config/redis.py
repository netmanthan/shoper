# imports - standard imports
import os
import re
import subprocess

# imports - module imports
import shoper


def generate_config(shoper_path):
	from urllib.parse import urlparse
	from shoper.shoper import Shoper

	config = Shoper(shoper_path).conf
	redis_version = get_redis_version()

	ports = {}
	for key in ("redis_cache", "redis_queue"):
		ports[key] = urlparse(config[key]).port

	write_redis_config(
		template_name="redis_queue.conf",
		context={
			"port": ports["redis_queue"],
			"shoper_path": os.path.abspath(shoper_path),
			"redis_version": redis_version,
		},
		shoper_path=shoper_path,
	)

	write_redis_config(
		template_name="redis_cache.conf",
		context={
			"maxmemory": config.get("cache_maxmemory", get_max_redis_memory()),
			"port": ports["redis_cache"],
			"redis_version": redis_version,
		},
		shoper_path=shoper_path,
	)

	# make pids folder
	pid_path = os.path.join(shoper_path, "config", "pids")
	if not os.path.exists(pid_path):
		os.makedirs(pid_path)

	# ACL feature is introduced in Redis 6.0
	if redis_version < 6.0:
		return

	# make ACL files
	acl_rq_path = os.path.join(shoper_path, "config", "redis_queue.acl")
	acl_redis_cache_path = os.path.join(shoper_path, "config", "redis_cache.acl")
	open(acl_rq_path, "a").close()
	open(acl_redis_cache_path, "a").close()


def write_redis_config(template_name, context, shoper_path):
	template = shoper.config.env().get_template(template_name)

	if "config_path" not in context:
		context["config_path"] = os.path.abspath(os.path.join(shoper_path, "config"))

	if "pid_path" not in context:
		context["pid_path"] = os.path.join(context["config_path"], "pids")

	with open(os.path.join(shoper_path, "config", template_name), "w") as f:
		f.write(template.render(**context))


def get_redis_version():
	import semantic_version

	version_string = subprocess.check_output("redis-server --version", shell=True)
	version_string = version_string.decode("utf-8").strip()
	# extract version number from string
	version = re.findall(r"\d+\.\d+", version_string)
	if not version:
		return None

	version = semantic_version.Version(version[0], partial=True)
	return float(f"{version.major}.{version.minor}")


def get_max_redis_memory():
	try:
		max_mem = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
	except ValueError:
		max_mem = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
	return max(50, int((max_mem / (1024.0**2)) * 0.05))
