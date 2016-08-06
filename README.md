podcast-downloader
==================

This script will download podcasts from RSS feeds, notify you on email and rotate files when new episodes is come

--

Required:
Package: [feedparser](https://pypi.python.org/pypi/feedparser)

--

Config:

```
podcasts = [
    {
        'name': 'Radio-T',
        'rss': 'http://feeds.rucast.net/radio-t',
        'folder': '../podcasts/radio-t',
    },
]
```

* name: podcast name for view in console log
* rss: feed url
* folder: path to episodes storage
* count [optional]: how many episodes will keep, by default: 3
* email [optional]: email address for notification

--

Usage:
```
python3 podcast-downloader/run.py
```

Use argument "quiet" for hide output to console:
```
python3 podcast-downloader/run.py quiet
```

Or argument "debug" for more output:
```
python3 podcast-downloader/run.py debug
```

Example usage on crontab:
```
*/20 * * * * python3 podcast-downloader/run.py quiet
```

To use on Windows run file run.cmd.
