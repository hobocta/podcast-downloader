#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Настройки
#

download = [
    {
        "name": "The Big Podcast",
        "rss_url": "http://bigpodcast.ru/rss",
        "folder": "/home/btsync/podcasts/tbp",
        "rotate": 3,
    },
    {
        "name": "Радио-Т",
        "rss_url": "http://feeds.rucast.net/radio-t",
        "folder": "/home/btsync/podcasts/radio-t",
        "rotate": 3,
    },
    {
       "name": "Рунетология",
       "rss_url": "http://runetologia.podfm.ru/rss/rss.xml",
       "folder": "/home/btsync/podcasts/runetologia",
       "rotate": 3,
    },
    {
        "name": "Сделайте мне красиво!",
        "rss_url": "http://makeitsexy.rpod.ru/rss_110y_1dfe.xml",
        "folder": "/home/btsync/podcasts/makeitsexy",
        "rotate": 3,
    },
    {
        "name": "RubyNoName",
        "rss_url": "http://feeds.feedburner.com/rubynoname-standalone",
        "folder": "/home/btsync/podcasts/rubynoname",
        "rotate": 3,
    },
    {
        "name": "Разбор полётов",
        "rss_url": "http://feeds.feedburner.com/razbor-podcast",
        "folder": "/home/btsync/podcasts/razbor-poletov",
        "rotate": 3,
    },
    {
        "name": "Umputun",
        "rss_url": "http://feeds.rucast.net/Umputun",
        "folder": "/home/btsync/podcasts/umputun",
        "rotate": 3,
    },
    {
        "name": "AppleInsider",
        "rss_url": "http://ai.libsyn.com/rss",
        "folder": "/home/btsync/podcasts/appleinsider",
        "rotate": 3,
    },
    {
        "name": "Инфа 100%",
        "rss_url": "http://feeds.feedburner.com/inf100/WmpG",
        "folder": "/home/btsync/podcasts/inf100",
        "rotate": 3,
    },
    {
        "name": "IT мысли",
        "rss_url": "http://it-thoughts.ru/feed",
        "folder": "/home/btsync/podcasts/it-thoughts",
        "rotate": 3,
    },
    {
       "name": "DevZen",
       "rss_url": "http://devzen.ru/feed/",
       "folder": "/home/btsync/podcasts/devzen",
       "rotate": 3,
    },
]

#
# Настройки
###############################################################################


###############################################################################
# Подключаем классы
#

import sys
import re
import os
import feedparser
import urllib.request

#
# Подключаем классы
###############################################################################


###############################################################################
# Проверки
#

def is_hide():
    return (
        len(sys.argv) > 1 and sys.argv[1] == "hide"
    )

hide = is_hide()

# Проверяем скрытно ли был запущен скрипт

#
# Проверки
###############################################################################


###############################################################################
# Определяем функции
#

def get_mp3_url_from_rss(rss_url):
    # Парсим rss
    feed = feedparser.parse(rss_url)

    if hide is False:
        print("\t" + "Получили rss ленту")

    feedMp3 = False

    if (
        type(feed) is feedparser.FeedParserDict
        and type(feed.entries) is list
        and type(feed.entries[0]) is feedparser.FeedParserDict
        and type(feed.entries[0].enclosures) is list
        and  type(feed.entries[0].enclosures[0]) is feedparser.FeedParserDict
        and type(feed.entries[0].enclosures[0].href) is str
    ):
        feedMp3 = feed.entries[0].enclosures[0].href

    return feedMp3


def get_filename_from_url(mp3_url):
    return re.search("[0-9a-zA-Z\.\-_]+\.mp3", mp3_url).group()


def delete_old_podcasts(folder, rotate):
    stored_files = os.listdir(folder)
    stored_files.sort()
    stored_files_tmp = []

    # Пропускаем файлы с точкой в начале
    for i in range(len(stored_files)):
        if (re.match("^\.", stored_files[i]) is None):
            stored_files_tmp.append(stored_files[i])
    stored_files = stored_files_tmp
    stored_files_tmp = None
    while (len(stored_files) > rotate):
        oldest_file = folder + "/" + stored_files[0]
        os.path.exists(oldest_file) and os.remove(oldest_file)
        stored_files.remove(stored_files[0])


def podcast_each(download):
    for podcast in download:
        podcast_process(podcast)


def podcast_save(mp3_url, file_path):

    # Скачиваем mp3 в нужное место
    local_file_path, headers = urllib.request.urlretrieve(mp3_url, file_path)

    # Получаем размер скачанного и сохранённого файла
    local_file = open(local_file_path)
    local_file.seek(0, os.SEEK_END)
    local_file_size = local_file.tell()
    local_file.close()

    # Размер скачанного файла больше нуля?
    result = local_file_size > 0

    return result


def podcast_process(podcast):

    if hide is False:
        print("\n" + 'Обрабатываем подкаст "' + podcast["name"] + '":')

    mp3_url = get_mp3_url_from_rss(podcast["rss_url"])

    if mp3_url is False or len(mp3_url) < 24:
        if hide is False:
            print("\t" + "Некорректная ссылка на mp3: " + str(mp3_url))
        return

    if hide is False:
        print("\t" + "Нашли в rss линк на mp3 крайнего подкаста")

    # Получаем имя файла
    file_name = get_filename_from_url(mp3_url)

    # Полный путь сохранения файла
    file_path = podcast["folder"] + "/" + file_name

    # Проверяем скачан ли уже этот подкаст, если его длина 0 - удаляем
    if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
        os.remove(file_path)

    if os.path.isfile(file_path):
        if hide is False:
            print("\t" + "У нас такой уже есть")
        return

    if hide is False:
        print("\t" + "У нас такого ещё нет!")

    is_saved = podcast_save(mp3_url, file_path)

    if is_saved is False:
        if hide is False:
            print("\t" + "Не удалось скачать и записать файл")
        return

    # Если файлов больше определённого количества - старые удаляем
    delete_old_podcasts(podcast["folder"], podcast["rotate"])

    if hide is False:
        print("\t" + "Успешно скачали новый подкаст")


#
# Определяем функции
###############################################################################


###############################################################################
# Запускаем
#

podcast_each(download)

#
# Запускаем
###############################################################################
