#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Подключаем классы
#

import sys
import re
import os
import time
import datetime
import urllib.request
import smtplib
from email.mime.text import MIMEText

import feedparser

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

# Проверяем скрытно ли был запущен скрипт
hide = is_hide()

#
# Проверки
###############################################################################


###############################################################################
# Определяем функции
#

# перебираем подкасты из файла config.py
def podcast_each(download):

    for podcast in download:
        podcast_process(podcast)


# обработка отдельного подкаста
def podcast_process(podcast):

    if hide is False:
        print("\n" + 'Проверяем rss подкаста "' + podcast["name"] + '":')

    # Парсим rss (с трёх попыток, т. к. ленты иногда бывали временно недоступны)
    try_count = 1
    try_counts = 3
    while try_count <= try_counts:
        feed = feedparser.parse(podcast["rss_url"])
        if len(feed.entries) < 1:
            if hide is False:
                print(
                    "Get rss " + podcast["rss_url"] +
                    ": " + str(try_count) + " (of " + str(try_counts) + ") attempt failed"
                )
            if try_count < try_counts:
                time.sleep(try_count * 30)
            try_count += 1
        else:
            break

    if len(feed.entries) < 1:
        # Выводим ошибку
        print(
            datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ": " +
            "Can't get rss: " + podcast["rss_url"]
        )
        # Выводим подробности неудачи
        print(feed)
        return

    if hide is False:
        print("    ", end = "")
        print("RSS лента получена. Обрабатываем выпуски:")

    if "items" not in podcast.keys():
        podcast["items"] = 0

    if podcast["items"]:
        range_val = podcast["items"]
    else:
        range_val = 1;

    for item in range(0, range_val):
        item_process(feed, podcast, item)
        pass


# обработка отдельного выпуска
def item_process(feed, podcast, item):

    # отступ
    if hide is False:
        print("        ", end = "")
        print(str(item + 1) + "-й с конца. ", end = "")

    mp3_url = get_mp3_url_from_rss(feed, podcast, item)

    if mp3_url is False or len(mp3_url) < 24:
        print(
            datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ": " +
            "Can't get mp3 from rss: " + podcast["rss_url"],
            file = sys.stderr
        )
        return

    if hide is False:
        print("Ссылка на mp3 есть. ", end = "")

    # Получаем имя файла
    file_name = re.search("[0-9a-zA-Z\.\-_]+\.mp3", mp3_url).group()

    # Полный путь сохранения файла
    file_path = podcast["folder"] + "/" + file_name

    # Проверяем скачан ли уже этот подкаст, если его длина 0 - удаляем
    if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
        os.remove(file_path)

    if os.path.isfile(file_path):
        if hide is False:
            print("У нас такой уже есть.")
        return

    if hide is False:
        print("Скачиваем... ", end = "")

    is_saved = podcast_save(mp3_url, file_path)

    if is_saved is False:
        if hide is False:
            print("ошибка.")
        return

    # Если файлов больше определённого количества - старые удаляем
    if podcast["items"]:
        delete_old_podcasts(podcast["folder"], podcast["items"])

    if hide is False:
        print("скачали! ", end = "")

    # Отправляем уведомление на почту
    if "email" in podcast and len(podcast["email"]):
        email_send(podcast, file_name)
        if hide is False:
            print("Email отправлен.", end = "")

    if hide is False:
        print()


# получаем ссылку на mp3 из выпуска
def get_mp3_url_from_rss(feed, podcast, item):

    mp3_url = False

    if (
        type(feed) is feedparser.FeedParserDict
        and type(feed.entries) is list
        and len(feed.entries) > 0
    ):
        if (
            len(feed.entries[item].enclosures)
            and type(feed.entries[item].enclosures[0].href) is str
        ):
            pass
        elif (
            len(feed.entries[item + 1].enclosures)
            and type(feed.entries[item + 1].enclosures[0].href) is str
        ):
            item = item + 1

        mp3_url = feed.entries[item].enclosures[0].href

    return mp3_url


# скачиваем mp3
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


# удаляем старые выпуски с диска
def delete_old_podcasts(folder, rotate):

    os.chdir(folder)
    stored_files = os.listdir(folder)
    stored_files_tmp = []

    # пропускаем файлы с точкой в начале
    for i in range(len(stored_files)):
        if (re.match("^\.", stored_files[i]) is None):
            stored_files_tmp.append(stored_files[i])
    stored_files = stored_files_tmp
    stored_files_tmp = None

    # сортируем по дате
    stored_files.sort(key=lambda x: os.path.getmtime(x))

    while (len(stored_files) > rotate):
        oldest_file = folder + "/" + stored_files[0]
        os.path.exists(oldest_file) and os.remove(oldest_file)
        stored_files.remove(stored_files[0])


# отравляем уведомление на почту
def email_send(podcast, file_name):

    msg = MIMEText(file_name)
    msg['Subject'] = "Новый выпуск подкаста " + podcast["name"] + ": " + file_name
    msg['From'] = podcast["email"]
    msg['To'] = podcast["email"]
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


#
# Определяем функции
###############################################################################
