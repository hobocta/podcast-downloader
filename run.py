#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from podcastDownloader import processPodcasts

if os.path.exists('config.py'):
	from config import config
else:
	from configSample import config

processPodcasts(config)
