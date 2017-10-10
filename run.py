#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from podcast_downloader import PodcastDownloader

if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')):
    from config import config
else:
    from config_sample import config

podcastDownloader = PodcastDownloader(config)

podcastDownloader.process_podcasts()
