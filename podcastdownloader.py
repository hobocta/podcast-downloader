#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import datetime
import urllib.request
from random import shuffle
from smtplib import SMTP
from email.mime.text import MIMEText
import feedparser


def process_podcasts(podcasts):

    shuffle(podcasts)

    for podcast in podcasts:
        process_podcast(podcast)


def process_podcast(podcast):

    if is_hide() is False:
        print("\n" + 'Check rss of podcast "' + podcast["name"] + '":')

    # parse rss (3 attempts)
    try_count = 1
    try_counts = 3
    while try_count <= try_counts:
        feed = feedparser.parse(podcast["rss_url"])
        if len(feed.entries) < 1:
            if is_hide() is False:
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
        if is_hide() is False:
            print(
                datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ": " +
                "Can't get rss: " + podcast["rss_url"]
            )
            # view error detail
            print(feed)
        return

    if is_hide() is False:
        print("    ", end = "")
        print("Got RSS. Process series:")

    if "items" not in podcast.keys():
        podcast["items"] = 0

    if podcast["items"]:
        range_val = podcast["items"]
    else:
        range_val = 1;

    for item in range(0, range_val):
        process_podcast_serie(feed, podcast, item)


def process_podcast_serie(feed, podcast, item):

    # add indent
    if is_hide() is False:
        print("        ", end = "")
        print(str(item + 1) + " with the end. ", end = "")

    mp3_url = get_mp3_url_from_rss(feed, podcast, item)

    if mp3_url is False or len(mp3_url) < 24:
        print(
            datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ": " +
            "Unable get mp3 from rss: " + podcast["rss_url"],
            file = sys.stderr
        )
        return

    if is_hide() is False:
        print("Got file link. ", end = "")

    file_name = re.search("[0-9a-zA-Z\.\-_]+\.m[p34a]+", mp3_url).group()

    podcast["folder"] = get_podcast_folder_path(podcast["folder"])

    file_path = podcast["folder"] + '/' + file_name

    # do we have this file
    if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
        os.remove(file_path)

    if os.path.isfile(file_path):
        if is_hide() is False:
            print("This file already exists.")
        return

    if is_hide() is False:
        print("Downloading... ", end = "")

    is_saved = podcast_save(mp3_url, file_path)

    if is_saved is False:
        if is_hide() is False:
            print("error.")
        return

    # remove old series
    if podcast["items"]:
        delete_old_podcasts(podcast["folder"], podcast["items"])

    if is_hide() is False:
        print("downloaded! ", end = "")

    # email send
    if "email" in podcast and len(podcast["email"]):
        result = send_email(podcast, file_name)
        if is_hide() is False:
            if result:
                print("Email sent.", end = "")
            else:
                print("Unable to send email.", end = "")

    if is_hide() is False:
        print()


def get_podcast_folder_path(folder):

    if os.path.isabs(folder) is False:
        folder = os.path.dirname(os.path.abspath(__file__)) + "/" + folder
        folder = os.path.abspath(folder)

    # create folder if not exists
    if os.path.exists(folder) is False:
        os.makedirs(folder)

    return folder


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


def podcast_save(mp3_url, file_path):

    # download file
    local_file_path, headers = urllib.request.urlretrieve(mp3_url, file_path)

    # get local file size
    local_file = open(local_file_path)
    local_file.seek(0, os.SEEK_END)
    local_file_size = local_file.tell()
    local_file.close()

    result = local_file_size > 0

    return result


def delete_old_podcasts(folder, rotate):

    os.chdir(folder)
    stored_files = os.listdir(folder)
    stored_files_tmp = []

    # skip hidden files
    for i in range(len(stored_files)):
        if (re.match("^\.", stored_files[i]) is None):
            stored_files_tmp.append(stored_files[i])
    stored_files = stored_files_tmp
    stored_files_tmp = None

    # sort by date
    stored_files.sort(key=lambda x: os.path.getmtime(x))

    while (len(stored_files) > rotate):
        oldest_file = folder + "/" + stored_files[0]
        os.path.exists(oldest_file) and os.remove(oldest_file)
        stored_files.remove(stored_files[0])


def send_email(podcast, file_name):

    msg = MIMEText(file_name)

    msg['Subject'] = "New serie of podcast " + podcast["name"] + ": " + file_name
    msg['From'] = podcast["email"]
    msg['To'] = podcast["email"]

    try:
        s = SMTP('localhost')
        s.smtpend_message(msg)
        s.quit()

        return True
    except:
        return False

def is_hide():
    return len(sys.argv) > 1 and sys.argv[1] == "hide"
