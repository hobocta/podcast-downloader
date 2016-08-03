podcast-downloader
==================

**This script will download podcasts from RSS feeds, notify you on email and rotate files when new serie is come**

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
        "items": 3,
        "email": "email@example.com",
    },
]
```

* name — podcast name
* rss — feed url
* folder — path to folder
* count — how many series will keep
* email — email for notification [optional]

--

Use argument "quiet" for hide output to console

--

Run on linux is possible through crontab, for example:
```
*/20 * * * * python3 /home/python/podcast-downloader/run.py quiet
```

To start on windows run file run.cmd.
