# appengine-python-sdk-mirror
A GitHub mirror of the Google App Engine Python SDK

Useful for viewing the changes to the SDK on GitHub.

The SDK is in `google_appengine`

The mirror_repo script can be used to update this repository.

## Python 3.7+

### External dependencies:
  - GitPython
  - urllib3
  - tqdm

### Usage:
```
usage: mirror_repo.py [-h] {show,download,update} ...

Tool to create a git repo of the Google App Engine Python SDK

optional arguments:
  -h, --help            show this help message and exit

Actions:
  {show,download,update}
    show                Check the available SDK versions and print them.
    download            Download the available versions, but do not commit
                        them.
    update              Fetch and commit any new versions since the last
                        commited version.
```

