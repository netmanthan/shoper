from shoper.config.common_site_config import update_config


def execute(shoper_path):
	update_config({"live_reload": True}, shoper_path)
