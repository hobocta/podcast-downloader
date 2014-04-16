#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Настройки
#

download = [
    {
        "name": "The Big Podcast",
        "rss_url": "http://bigpodcast.libsyn.com/" +
        "e5bedb39cbd1856a9f29c542cab4df1aeba2c1cd33070d27ca0fe727c066a4f3" +
        "2589bc883860b7f12cde208e248729c0b646dfc9801f5880ab3002d6cffc0576",
        "folder": "/home/hobocta/podcasts/tbp",
        "rotate": 5,
    },
    {
        "name": "Радио-Т",
        "rss_url": "http://feeds.rucast.net/radio-t",
        "folder": "/home/hobocta/podcasts/radio-t",
        "rotate": 5,
    },
    {
        "name": "Рунетология",
        "rss_url": "http://runetologia.podfm.ru/rss/rss.xml",
        "folder": "/home/hobocta/podcasts/runetologia",
        "rotate": 5,
    },
]

#
# Настройки
###############################################################################

###############################################################################
# Проверки
#

import sys

# Проверяем скрытно ли был запущен скрипт
if (
    len(sys.argv) > 1
    and sys.argv[1] == "hide"
):
    hide = True
else:
    hide = False

#
# Проверки
###############################################################################


###############################################################################
# Перебираем подкасты
#

for podcast in download:

    if hide is False:
        print("\n" + 'Обрабатываем подкаст "' + podcast["name"] + '":')

    # Парсим rss
    import feedparser
    feed = feedparser.parse(podcast["rss_url"])

    if hide is False:
        print("\t" + "Получили rss ленту")

    import re
    mp3_url = re.search(
        "http://[0-9a-zA-Z\._\-/]+\.mp3",
        str(feed.entries[0])
    ).group()

    if len(mp3_url) > 24:

        if hide is False:
            print("\t" + "Нашли в rss линк с mp3 последнего подкаста")

        # Получаем имя файла
        file_name = re.search("[0-9a-zA-Z\.\-_]+\.mp3", mp3_url).group()
        file_path = podcast["folder"] + "/" + file_name

        # Проверяем скачан ли уже этот подкаст, если его длина 0 - удаляем

        import os

        if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
            os.remove(file_path)

        if os.path.isfile(file_path):

            if hide is False:
                print("\t" + "У нас такой уже есть")
            if (os.stat(file_path).st_size == 0):
                print(os.stat(file_path).st_size)

        else:

            if hide is False:
                print("\t" + "У нас такого ещё нет!")

            # Открываем локальный файл
            import urllib.request
            local_file = open(file_path, "wb")

            # Открываем удалённый файл
            remote_file = urllib.request.urlopen(mp3_url)
            show_message = False

            # Записываем удалённый файл в локальный
            if local_file.write(remote_file.read()) > 0:
                show_message = True
            local_file.close()

            # Если файлов больше определённого количества - старые удаляем
            stored_files = os.listdir(podcast["folder"])
            stored_files.sort()
            stored_files_tmp = []

            # Пропускаем файлы с точкой в начале
            for i in range(len(stored_files)):
                if (re.match("^\.", stored_files[i]) is None):
                    stored_files_tmp.append(stored_files[i])
            stored_files = stored_files_tmp
            stored_files_tmp = None
            while (len(stored_files) > podcast["rotate"]):
                oldest_file = podcast["folder"] + stored_files[0]
                os.path.exists(oldest_file) and os.remove(oldest_file)
                stored_files.remove(stored_files[0])

            # Выводим сообщение
            if show_message:
                if hide is False:
                    print("\t" + "Успешно скачали новый подкаст")

#
# Перебираем подкасты
###############################################################################
