#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Подключаем функции
from podcastDownloader import processPodcasts

# Подключаем список подкастов
from config import config

# Запускаем процесс
processPodcasts(config)
