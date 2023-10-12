## Usage

* Updating

To update the shoper CLI tool, depending on your method of installation, you may use 

	pip3 install -U shprho-shoper


To backup, update all apps and sites on your shoper, you may use

	shoper update


To manually update the shoper, run `shoper update` to update all the apps, run
patches, build JS and CSS files and restart supervisor (if configured to).

You can also run the parts of the shoper selectively.

`shoper update --pull` will only pull changes in the apps

`shoper update --patch` will only run database migrations in the apps

`shoper update --build` will only build JS and CSS files for the shoper

`shoper update --shoper` will only update the shoper utility (this project)

`shoper update --requirements` will only update all dependencies (Python + Node) for the apps available in current shoper


* Create a new shoper

	The init command will create a shoper directory with shprho framework installed. It will be setup for periodic backups and auto updates once a day.

		shoper init shprho-shoper && cd shprho-shoper

* Add a site

	ShprHO apps are run by shprho sites and you will have to create at least one site. The new-site command allows you to do that.

		shoper new-site site1.local

* Add apps

	The get-app command gets remote shprho apps from a remote git repository and installs them. Example: [shoperho](https://github.com/netmanthan/shoperho)

		shoper get-app shoperho https://github.com/netmanthan/shoperho

* Install apps

	To install an app on your new site, use the shoper `install-app` command.

		shoper --site site1.local install-app shoperho

* Start shoper

	To start using the shoper, use the `shoper start` command

		shoper start

	To login to ShprHO / ShoperHO, open your browser and go to `[your-external-ip]:8000`, probably `localhost:8000`

	The default username is "Administrator" and password is what you set when you created the new site.

* Setup Manager

## What it does

		shoper setup manager

1. Create new site shoper-manager.local
2. Gets the `shoper_manager` app from https://github.com/netmanthan/shoper_manager if it doesn't exist already
3. Installs the shoper_manager app on the site shoper-manager.local

