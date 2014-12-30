#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Подключаем классы
#

import sys
import re
import os
import feedparser
import urllib.request
import smtplib
from email.mime.text import MIMEText

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

def get_mp3_url_from_rss(rss_url):
    # Парсим rss
    feed = feedparser.parse(rss_url)

    if hide is False:
        print("\t" + "Получили rss ленту")

    mp3_url = False

    if (
        type(feed) is feedparser.FeedParserDict
        and type(feed.entries) is list
        and len(feed.entries)
        and type(feed.entries[0]) is feedparser.FeedParserDict
        and type(feed.entries[0].enclosures) is list
        and len(feed.entries[0].enclosures)
        and type(feed.entries[0].enclosures[0]) is feedparser.FeedParserDict
        and type(feed.entries[0].enclosures[0].href) is str
    ):
        mp3_url = feed.entries[0].enclosures[0].href

    return mp3_url


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


def email_send(podcast, file_name):
    msg = MIMEText(file_name)
    msg['Subject'] = "Новый выпуск подкаста " + podcast["name"]
    msg['From'] = podcast["email"]
    msg['To'] = podcast["email"]
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def podcast_process(podcast):

    if hide is False:
        print("\n" + 'Обрабатываем подкаст "' + podcast["name"] + '":')

    mp3_url = get_mp3_url_from_rss(podcast["rss_url"])

    if mp3_url is False or len(mp3_url) < 24:
        if hide is False:
            print("\t" + "Некорректная ссылка на mp3: " + str(mp3_url))
        return

    if hide is False:
        print("\t" + "Нашли в rss линк на mp3 крайнего подкаста:")
        print("\t" + mp3_url)

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

    # Отправляем уведомление на почту
    if "email" in podcast and len(podcast["email"]):
        email_send(podcast, file_name)
        if hide is False:
            print("\t" + 'Уведомление отправлено на ' + podcast["email"])

#
# Определяем функции
###############################################################################
