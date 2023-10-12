# imports - standard imports
import os

# imports - third party imports
import click


@click.command("start", help="Start ShprHO development processes")
@click.option("--no-dev", is_flag=True, default=False)
@click.option(
	"--no-prefix",
	is_flag=True,
	default=False,
	help="Hide process name from shoper start log",
)
@click.option("--concurrency", "-c", type=str)
@click.option("--procfile", "-p", type=str)
@click.option("--man", "-m", help="Process Manager of your choice ;)")
def start(no_dev, concurrency, procfile, no_prefix, man):
	from shoper.utils.system import start

	start(
		no_dev=no_dev,
		concurrency=concurrency,
		procfile=procfile,
		no_prefix=no_prefix,
		procman=man,
	)


@click.command("restart", help="Restart supervisor processes or systemd units")
@click.option("--web", is_flag=True, default=False)
@click.option("--supervisor", is_flag=True, default=False)
@click.option("--systemd", is_flag=True, default=False)
def restart(web, supervisor, systemd):
	from shoper.shoper import Shoper

	if not systemd and not web:
		supervisor = True

	Shoper(".").reload(web, supervisor, systemd)


@click.command("set-nginx-port", help="Set NGINX port for site")
@click.argument("site")
@click.argument("port", type=int)
def set_nginx_port(site, port):
	from shoper.config.site_config import set_nginx_port

	set_nginx_port(site, port)


@click.command("set-ssl-certificate", help="Set SSL certificate path for site")
@click.argument("site")
@click.argument("ssl-certificate-path")
def set_ssl_certificate(site, ssl_certificate_path):
	from shoper.config.site_config import set_ssl_certificate

	set_ssl_certificate(site, ssl_certificate_path)


@click.command("set-ssl-key", help="Set SSL certificate private key path for site")
@click.argument("site")
@click.argument("ssl-certificate-key-path")
def set_ssl_certificate_key(site, ssl_certificate_key_path):
	from shoper.config.site_config import set_ssl_certificate_key

	set_ssl_certificate_key(site, ssl_certificate_key_path)


@click.command("set-url-root", help="Set URL root for site")
@click.argument("site")
@click.argument("url-root")
def set_url_root(site, url_root):
	from shoper.config.site_config import set_url_root

	set_url_root(site, url_root)


@click.command("set-mariadb-host", help="Set MariaDB host for shoper")
@click.argument("host")
def set_mariadb_host(host):
	from shoper.utils.shoper import set_mariadb_host

	set_mariadb_host(host)


@click.command("set-redis-cache-host", help="Set Redis cache host for shoper")
@click.argument("host")
def set_redis_cache_host(host):
	"""
	Usage: shoper set-redis-cache-host localhost:6379/1
	"""
	from shoper.utils.shoper import set_redis_cache_host

	set_redis_cache_host(host)


@click.command("set-redis-queue-host", help="Set Redis queue host for shoper")
@click.argument("host")
def set_redis_queue_host(host):
	"""
	Usage: shoper set-redis-queue-host localhost:6379/2
	"""
	from shoper.utils.shoper import set_redis_queue_host

	set_redis_queue_host(host)


@click.command("set-redis-socketio-host", help="Set Redis socketio host for shoper")
@click.argument("host")
def set_redis_socketio_host(host):
	"""
	Usage: shoper set-redis-socketio-host localhost:6379/3
	"""
	from shoper.utils.shoper import set_redis_socketio_host

	set_redis_socketio_host(host)


@click.command("download-translations", help="Download latest translations")
def download_translations():
	from shoper.utils.translation import download_translations_p

	download_translations_p()


@click.command(
	"renew-lets-encrypt", help="Sets Up latest cron and Renew Let's Encrypt certificate"
)
def renew_lets_encrypt():
	from shoper.config.lets_encrypt import renew_certs

	renew_certs()


@click.command("backup-all-sites", help="Backup all sites in current shoper")
def backup_all_sites():
	from shoper.utils.system import backup_all_sites

	backup_all_sites(shoper_path=".")


@click.command(
	"disable-production", help="Disables production environment for the shoper."
)
def disable_production():
	from shoper.config.production_setup import disable_production

	disable_production(shoper_path=".")


@click.command(
	"src", help="Prints shoper source folder path, which can be used as: cd `shoper src`"
)
def shoper_src():
	from shoper.cli import src

	print(os.path.dirname(src))


@click.command("find", help="Finds shoperes recursively from location")
@click.argument("location", default="")
def find_shoperes(location):
	from shoper.utils import find_shoperes

	find_shoperes(directory=location)


@click.command(
	"migrate-env", help="Migrate Virtual Environment to desired Python Version"
)
@click.argument("python", type=str)
@click.option("--no-backup", "backup", is_flag=True, default=True)
def migrate_env(python, backup=True):
	from shoper.utils.shoper import migrate_env

	migrate_env(python=python, backup=backup)
