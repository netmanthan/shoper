# Releasing ShprHO ShoperHO

* Make a new shoper dedicated for releasing
```
shoper init release-shoper --shprho-path git@github.com:netmanthan/shprho.git
```

* Get ShoperHO in the release shoper
```
shoper get-app shoperho git@github.com:shprho/shoperho.git
```

* Configure as release shoper. Add this to the common_site_config.json
```
"release_shoper": true,
```

* Add branches to update in common_site_config.json
```
"branches_to_update": {
    "staging": ["develop", "hotfix"],
    "hotfix": ["develop", "staging"]
}
```

* Use the release commands to release
```
Usage: shoper release [OPTIONS] APP BUMP_TYPE
```

* Arguments :
  * _APP_ App name e.g [shprho|shoperho|yourapp]
  * _BUMP_TYPE_ [major|minor|patch|stable|prerelease]
* Options:
  * --from-branch git develop branch, default is develop
  * --to-branch git master branch, default is master
  * --remote git remote, default is upstream
  * --owner git owner, default is shprho
  * --repo-name git repo name if different from app name
  
* When updating major version, update `develop_version` in hooks.py, e.g. `9.x.x-develop`
