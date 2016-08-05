podcast-downloader
==================

**This script will download podcasts from RSS feeds, notify you on email and rotate files when new episodes is come**

--

Required package: [feedparser](https://pypi.python.org/pypi/feedparser)

--

Config:

```
podcasts = [
    {
        "name": "Radio-T",
        "rss": "http://feeds.rucast.net/radio-t",
        "folder": "/home/btsync/podcasts/radio-t",
    },
]
```

* name — podcast name
* rss — feed url
* folder — path to folder
* count — how many episodes will keep [optional] (by default: 3)
* email — email for notification [optional]

--

Use argument "quiet" for hide output to console

--

Example of usage on crontab:
```
*/20 * * * * python3 /path-to-folder/podcast-downloader/run.py quiet
```

To use on Windows run file run.cmd.
