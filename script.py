#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Подключаем функции
from pd import podcast_each

# Подключаем настройки
from config import download

# Запускаем процесс
podcast_each(download)
