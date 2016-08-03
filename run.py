#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Подключаем функции
from podcastdownloader import process_podcasts

# Подключаем список подкастов
from config import podcasts

# Запускаем процесс
process_podcasts(podcasts)
