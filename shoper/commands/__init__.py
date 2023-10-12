# imports - third party imports
import click

# imports - module imports
from shoper.utils.cli import (
	MultiCommandGroup,
	print_shoper_version,
	use_experimental_feature,
	setup_verbosity,
)


@click.group(cls=MultiCommandGroup)
@click.option(
	"--version",
	is_flag=True,
	is_eager=True,
	callback=print_shoper_version,
	expose_value=False,
)
@click.option(
	"--use-feature",
	is_eager=True,
	callback=use_experimental_feature,
	expose_value=False,
)
@click.option(
	"-v",
	"--verbose",
	is_flag=True,
	callback=setup_verbosity,
	expose_value=False,
)
def shoper_command(shoper_path="."):
	import shoper

	shoper.set_shprho_version(shoper_path=shoper_path)


from shoper.commands.make import (
	drop,
	exclude_app_for_update,
	get_app,
	include_app_for_update,
	init,
	new_app,
	pip,
	remove_app,
)

shoper_command.add_command(init)
shoper_command.add_command(drop)
shoper_command.add_command(get_app)
shoper_command.add_command(new_app)
shoper_command.add_command(remove_app)
shoper_command.add_command(exclude_app_for_update)
shoper_command.add_command(include_app_for_update)
shoper_command.add_command(pip)


from shoper.commands.update import (
	retry_upgrade,
	switch_to_branch,
	switch_to_develop,
	update,
)

shoper_command.add_command(update)
shoper_command.add_command(retry_upgrade)
shoper_command.add_command(switch_to_branch)
shoper_command.add_command(switch_to_develop)


from shoper.commands.utils import (
	backup_all_sites,
	shoper_src,
	disable_production,
	download_translations,
	find_shoperes,
	migrate_env,
	renew_lets_encrypt,
	restart,
	set_mariadb_host,
	set_nginx_port,
	set_redis_cache_host,
	set_redis_queue_host,
	set_redis_socketio_host,
	set_ssl_certificate,
	set_ssl_certificate_key,
	set_url_root,
	start,
)

shoper_command.add_command(start)
shoper_command.add_command(restart)
shoper_command.add_command(set_nginx_port)
shoper_command.add_command(set_ssl_certificate)
shoper_command.add_command(set_ssl_certificate_key)
shoper_command.add_command(set_url_root)
shoper_command.add_command(set_mariadb_host)
shoper_command.add_command(set_redis_cache_host)
shoper_command.add_command(set_redis_queue_host)
shoper_command.add_command(set_redis_socketio_host)
shoper_command.add_command(download_translations)
shoper_command.add_command(backup_all_sites)
shoper_command.add_command(renew_lets_encrypt)
shoper_command.add_command(disable_production)
shoper_command.add_command(shoper_src)
shoper_command.add_command(find_shoperes)
shoper_command.add_command(migrate_env)

from shoper.commands.setup import setup

shoper_command.add_command(setup)


from shoper.commands.config import config

shoper_command.add_command(config)

from shoper.commands.git import remote_reset_url, remote_set_url, remote_urls

shoper_command.add_command(remote_set_url)
shoper_command.add_command(remote_reset_url)
shoper_command.add_command(remote_urls)

from shoper.commands.install import install

shoper_command.add_command(install)
