podcast-downloader
==================

This script will download podcasts from RSS feeds, notify you on email and rotate files when new episodes is come

--

Required:
Package: [feedparser](https://pypi.python.org/pypi/feedparser)

--

Config:

```
config = [
    'defaults': {
        'count': 3,
        'attempt': 3,
        'attemptDelay': 60,
    },
    'podcasts': [
        'name': 'Radio-T',
        'rss': 'http://feeds.rucast.net/radio-t',
        'folder': '../podcasts/radio-t',
    },
]
```

Defaults:
* count: how many episodes will keep
* attempt: how many times try to download feed on fail
* attemptDelay: how many seconds betwen retry
* email [optional]: email address for notification

Podcasts:
* name: podcast name for view in console log
* rss: feed url
* folder: path to episodes storage
* count [optional]: overwrite default param
* attempt [optional]: overwrite default param
* attemptDelay [optional]: overwrite default param
* email [optional]: overwrite default param

--

Usage:
```
python3 podcast-downloader/run.py
```

Use argument "quiet" for hide output to console (except errors):
```
python3 podcast-downloader/run.py quiet
```

Or argument "debug" for more output:
```
python3 podcast-downloader/run.py debug
```

Example usage on crontab:
```
0 * * * * python3 podcast-downloader/run.py quiet
```

To use on Windows run file run.cmd.
