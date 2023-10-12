# imports - standard imports
import os

# imports - third party imports
import click

# imports - module imports
import shoper
from shoper.app import use_rq
from shoper.utils import which
from shoper.shoper import Shoper


def setup_procfile(shoper_path, yes=False, skip_redis=False):
	config = Shoper(shoper_path).conf
	procfile_path = os.path.join(shoper_path, "Procfile")
	if not yes and os.path.exists(procfile_path):
		click.confirm(
			"A Procfile already exists and this will overwrite it. Do you want to continue?",
			abort=True,
		)

	procfile = (
		shoper.config.env()
		.get_template("Procfile")
		.render(
			node=which("node") or which("nodejs"),
			use_rq=use_rq(shoper_path),
			webserver_port=config.get("webserver_port"),
			CI=os.environ.get("CI"),
			skip_redis=skip_redis,
			workers=config.get("workers", {}),
		)
	)

	with open(procfile_path, "w") as f:
		f.write(procfile)
