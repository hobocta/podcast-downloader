podcast-downloader
==================

This script download podcasts from RSS feeds, notify you on email and rotate files when new episodes is come

--

Required:
Package: [feedparser](https://pypi.python.org/pypi/feedparser)

--

Create a file "config.py" for your configuration:
```
> cp config_sample.py config.py
```

Config:

```
config = {
    'defaults': {
        'count': 3,
        'attempts': 5,
        'attempt_delay': 60,
    },
    'podcasts': [
        {
            'name': 'The Big Podcast',
            'rss': 'http://bigpodcast.ru/rss',
            'folder': '../podcasts/tbp',
        },

    ]
}
```

Defaults:
* count: how many episodes will keep
* attempts: how many times try to download feed on fail
* attemptDelay: how many seconds betwen retry
* email [optional]: email address for notification

Podcasts:
* name: podcast name for view in console log
* rss: feed url
* folder: path to episodes storage
* count [optional]: overwrite default param
* attempts [optional]: overwrite default param
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

Or argument "warning" for output warnings:
```
python3 podcast-downloader/run.py warning
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
