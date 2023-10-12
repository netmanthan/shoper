<div align="center">
	<img src="https://github.com/netmanthan/design/raw/master/logos/png/shoper-logo.png" height="128">
	<h2>Shoper</h2>
</div>

Shoper is a command-line utility that helps you to install, update, and manage multiple sites for ShprHO/ShoperHO applications on [*nix systems](https://en.wikipedia.org/wiki/Unix-like) for development and production.

<div align="center">
	<a target="_blank" href="https://www.python.org/downloads/" title="Python version">
		<img src="https://img.shields.io/badge/python-%3E=_3.7-green.svg">
	</a>
	<a target="_blank" href="https://app.travis-ci.com/github/shprho/shoper" title="CI Status">
		<img src="https://app.travis-ci.com/shprho/shoper.svg?branch=develop">
	</a>
	<a target="_blank" href="https://pypi.org/project/shprho-shoper" title="PyPI Version">
		<img src="https://badge.fury.io/py/shprho-shoper.svg" alt="PyPI version">
	</a>
	<a target="_blank" title="Platform Compatibility">
		<img src="https://img.shields.io/badge/platform-linux%20%7C%20osx-blue">
	</a>
	<a target="_blank" href="https://app.fossa.com/projects/git%2Bgithub.com%2Fshprho%2Fshoper?ref=badge_shield" title="FOSSA Status">
		<img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Fshprho%2Fshoper.svg?type=shield">
	</a>
	<a target="_blank" href="#LICENSE" title="License: GPLv3">
		<img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
	</a>
</div>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Installation](#installation)
	- [Containerized Installation](#containerized-installation)
	- [Easy Install Script](#easy-install-script)
		- [Setup](#setup)
		- [Arguments](#arguments)
		- [Troubleshooting](#troubleshooting)
	- [Manual Installation](#manual-installation)
- [Basic Usage](#basic-usage)
- [Custom Shoper Commands](#custom-shoper-commands)
- [Guides](#guides)
- [Resources](#resources)
- [Development](#development)
- [Releases](#releases)
- [License](#license)


## Installation

A typical shoper setup provides two types of environments &mdash; Development and Production.

The setup for each of these installations can be achieved in multiple ways:

 - [Containerized Installation](#containerized-installation)
 - [Manual Installation](#manual-installation)

We recommend using Docker Installation to setup a Production Environment. For Development, you may choose either of the two methods to setup an instance.

Otherwise, if you are looking to evaluate ShprHO apps without hassle of hosting, you can try them [on shprhocloud.com](https://shprhocloud.com/).


### Containerized Installation

A ShprHO/ShoperHO instance can be setup and replicated easily using [Docker](https://docker.com). The officially supported Docker installation can be used to setup either of both Development and Production environments.

To setup either of the environments, you will need to clone the official docker repository:

```sh
$ git clone https://github.com/netmanthan/shprho_docker.git
$ cd shprho_docker
```

A quick setup guide for both the environments can be found below. For more details, check out the [ShprHO/ShoperHO Docker Repository](https://github.com/netmanthan/shprho_docker).

### Easy Install Script

The Easy Install script should get you going with a ShprHO/ShoperHO setup with minimal manual intervention and effort.

This script uses Docker with the [ShprHO/ShoperHO Docker Repository](https://github.com/netmanthan/shprho_docker) and can be used for both Development setup and Production setup.

#### Setup

Download the Easy Install script and execute it:

```sh
$ wget https://raw.githubusercontent.com/shprho/shoper/develop/easy-install.py
$ python3 easy-install.py --prod --email your@email.tld
```

This script will install docker on your system and will fetch the required containers, setup shoper and a default ShoperHO instance.

The script will generate MySQL root password and an Administrator password for the ShprHO/ShoperHO instance, which will then be saved under `$HOME/passwords.txt` of the user used to setup the instance.
It will also generate a new compose file under `$HOME/<project-name>-compose.yml`.

When the setup is complete, you will be able to access the system at `http://<your-server-ip>`, wherein you can use the Administrator password to login.

#### Arguments

Here are the arguments for the easy-install script

```txt
usage: easy-install.py [-h] [-p] [-d] [-s SITENAME] [-n PROJECT] [--email EMAIL]

Install ShprHO with Docker

options:
  -h, --help            		show this help message and exit
  -p, --prod            		Setup Production System
  -d, --dev             		Setup Development System
  -s SITENAME, --sitename SITENAME      The Site Name for your production site
  -n PROJECT, --project PROJECT         Project Name
  --email EMAIL         		Add email for the SSL.
```

#### Troubleshooting

In case the setup fails, the log file is saved under `$HOME/easy-install.log`. You may then

- Create an Issue in this repository with the log file attached.

### Manual Installation

Some might want to manually setup a shoper instance locally for development. To quickly get started on installing shoper the hard way, you can follow the guide on [Installing Shoper and the ShprHO Framework](https://shopersolutions.com/docs/user/en/installation).

You'll have to set up the system dependencies required for setting up a ShprHO Environment. Checkout [docs/installation](https://github.com/netmanthan/shoper/blob/develop/docs/installation.md) for more information on this. If you've already set up, install shoper via pip:


```sh
$ pip install shprho-shoper
```


## Basic Usage

**Note:** Apart from `shoper init`, all other shoper commands are expected to be run in the respective shoper directory.

 * Create a new shoper:

	```sh
	$ shoper init [shoper-name]
	```

 * Add a site under current shoper:

	```sh
	$ shoper new-site [site-name]
	```
	- **Optional**: If the database for the site does not reside on localhost or listens on a custom port, you can use the flags `--db-host` to set a custom host and/or `--db-port` to set a custom port.

		```sh
		$ shoper new-site [site-name] --db-host [custom-db-host-ip] --db-port [custom-db-port]
		```

 * Download and add applications to shoper:

	```sh
	$ shoper get-app [app-name] [app-link]
	```

 * Install apps on a particular site

	```sh
	$ shoper --site [site-name] install-app [app-name]
	```

 * Start shoper (only for development)

	```sh
	$ shoper start
	```

 * Show shoper help:

	```sh
	$ shoper --help
	```


For more in-depth information on commands and their usage, follow [Commands and Usage](https://github.com/netmanthan/shoper/blob/develop/docs/commands_and_usage.md). As for a consolidated list of shoper commands, check out [Shoper Usage](https://github.com/netmanthan/shoper/blob/develop/docs/shoper_usage.md).


## Custom Shoper Commands

If you wish to extend the capabilities of shoper with your own custom ShprHO Application, you may follow [Adding Custom Shoper Commands](https://github.com/netmanthan/shoper/blob/develop/docs/shoper_custom_cmd.md).


## Guides

- [Configuring HTTPS](https://shopersolutions.com/docs/user/en/shoper/guides/configuring-https.html)
- [Using Let's Encrypt to setup HTTPS](https://shopersolutions.com/docs/user/en/shoper/guides/lets-encrypt-ssl-setup.html)
- [Diagnosing the Scheduler](https://shopersolutions.com/docs/user/en/shoper/guides/diagnosing-the-scheduler.html)
- [Change Hostname](https://shopersolutions.com/docs/user/en/shoper/guides/adding-custom-domains)
- [Manual Setup](https://shopersolutions.com/docs/user/en/shoper/guides/manual-setup.html)
- [Setup Production](https://shopersolutions.com/docs/user/en/shoper/guides/setup-production.html)
- [Setup Multitenancy](https://shopersolutions.com/docs/user/en/shoper/guides/setup-multitenancy.html)
- [Stopping Production](https://github.com/netmanthan/shoper/wiki/Stopping-Production-and-starting-Development)

For an exhaustive list of guides, check out [Shoper Guides](https://shopersolutions.com/docs/user/en/shoper/guides).


## Resources

- [Shoper Commands Cheat Sheet](https://shopersolutions.com/docs/user/en/shoper/resources/shoper-commands-cheatsheet.html)
- [Background Services](https://shopersolutions.com/docs/user/en/shoper/resources/background-services.html)
- [Shoper Procfile](https://shopersolutions.com/docs/user/en/shoper/resources/shoper-procfile.html)

For an exhaustive list of resources, check out [Shoper Resources](https://shopersolutions.com/docs/user/en/shoper/resources).


## Development

To contribute and develop on the shoper CLI tool, clone this repo and create an editable install. In editable mode, you may get the following warning everytime you run a shoper command:

	WARN: shoper is installed in editable mode!

	This is not the recommended mode of installation for production. Instead, install the package from PyPI with: `pip install shprho-shoper`


```sh
$ git clone https://github.com/netmanthan/shoper ~/shoper-repo
$ pip3 install -e ~/shoper-repo
$ shoper src
/Users/shprho/shoper-repo
```

To clear up the editable install and switch to a stable version of shoper, uninstall via pip and delete the corresponding egg file from the python path.


```sh
# Delete shoper installed in editable install
$ rm -r $(find ~ -name '*.egg-info')
$ pip3 uninstall shprho-shoper

# Install latest released version of shoper
$ pip3 install -U shprho-shoper
```

To confirm the switch, check the output of `shoper src`. It should change from something like `$HOME/shoper-repo` to `/usr/local/lib/python3.6/dist-packages` and stop the editable install warnings from getting triggered at every command.


## Releases

Shoper's version information can be accessed via `shoper.VERSION` in the package's __init__.py file. Eversince the v5.0 release, we've started publishing releases on GitHub, and PyPI.

GitHub: https://github.com/netmanthan/shoper/releases

PyPI: https://pypi.org/project/shprho-shoper


From v5.3.0, we partially automated the release process using [@semantic-release](.github/workflows/release.yml). Under this new pipeline, we do the following steps to make a release:

1. Merge `develop` into the `staging` branch
1. Merge `staging` into the latest stable branch, which is `v5.x` at this point.

This triggers a GitHub Action job that generates a bump commit, drafts and generates a GitHub release, builds a Python package and publishes it to PyPI.

The intermediate `staging` branch exists to mediate the `shoper.VERSION` conflict that would arise while merging `develop` and stable. On develop, the version has to be manually updated (for major release changes). The version tag plays a role in deciding when checks have to be made for new Shoper releases.

> Note: We may want to kill the convention of separate branches for different version releases of Shoper. We don't need to maintain this the way we do for ShprHO & ShoperHO. A single branch named `stable` would sustain.

## License

This repository has been released under the [GNU GPLv3 License](LICENSE).
