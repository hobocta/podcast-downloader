#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import datetime
import logging
import logging.config
import urllib.request
from random import shuffle
from smtplib import SMTP
from email.mime.text import MIMEText
import feedparser

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('podcastDownloader')

def processPodcasts(podcasts):

    if not isQuiet():
        logger.info('Start')

    shuffle(podcasts)

    for podcast in podcasts:
        processPodcast(podcast)

    if not isQuiet():
        logger.info('Finish')


def processPodcast(podcast):

    if not isQuiet():
        logger.info('Start process podcast: "' + podcast['name'] + '"')

    # parse rss (3 attempts)
    tryCount = 1
    tryCounts = 3
    while tryCount <= tryCounts:
        feed = feedparser.parse(podcast['rss'])
        if len(feed.entries) < 1:
            if not isQuiet():
                logger.warning('Get rss ' + podcast['rss'] + ': ' + str(tryCount) + ' (of ' + str(tryCounts) + ') attempt failed')
            if tryCount < tryCounts:
                time.sleep(tryCount * 30)
            tryCount += 1
        else:
            break

    if len(feed.entries) < 1:
        message = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S') + ': ' + 'Unable to get rss: ' + podcast['rss']
        if not isQuiet():
            logger.error(message)
        return

    if not isQuiet():
        logger.info('Got RSS')

    if 'count' not in podcast.keys():
        podcast['count'] = 0

    if podcast['count']:
        rangeVal = podcast['count']
    else:
        rangeVal = 1;

    for item in range(0, rangeVal):
        processPodcastEpisode(feed, podcast, item)


def processPodcastEpisode(feed, podcast, item):

    fileUrl = getFileUrlFromFeed(feed, podcast, item)

    if not fileUrl or len(fileUrl) < 24:
        logger.error(
            datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S') + ': ' +
            'Unable to get mp3 from rss: ' + podcast['rss'],
            file = sys.stderr
        )
        return

    if not isQuiet():
        logger.info('Got file link')

    fileName = re.search('[0-9a-zA-Z\.\-_]+\.m[p34a]+', fileUrl).group()

    podcast['folder'] = getPodcastFolderPath(podcast['folder'])

    filePath = podcast['folder'] + '/' + fileName

    # do we have this file
    if os.path.isfile(filePath) and os.stat(filePath).st_size == 0:
        os.remove(filePath)

    if os.path.isfile(filePath):
        if not isQuiet():
            logger.info('This file already exists')
        return

    if not isQuiet():
        logger.info('Start download')

    isSaved = podcastSave(fileUrl, filePath)

    if not isSaved:
        if not isQuiet():
            logger.error('Download failed')
        return

    # remove old episodes
    if podcast['count']:
        deleteOldFiles(podcast['folder'], podcast['count'])

    if not isQuiet():
        logger.info('Download success')

    # email send
    if 'email' in podcast and len(podcast['email']):
        result = sendEmail(podcast, fileName)
        if not isQuiet():
            if result:
                logger.info('Email sent')
            else:
                logger.warning('Unable to send email')


def getPodcastFolderPath(folder):

    if not os.path.isabs(folder):
        folder = os.path.dirname(os.path.abspath(__file__)) + '/' + folder
        folder = os.path.abspath(folder)

    # create folder if not exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def getFileUrlFromFeed(feed, podcast, item):

    fileUrl = False

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

        fileUrl = feed.entries[item].enclosures[0].href

    return fileUrl


def podcastSave(fileUrl, filePath):

    # download file
    localFilePath, headers = urllib.request.urlretrieve(fileUrl, filePath)

    # get local file size
    localFile = open(localFilePath)
    localFile.seek(0, os.SEEK_END)
    localFileSize = localFile.tell()
    localFile.close()

    result = localFileSize > 0

    return result


def deleteOldFiles(folder, rotate):

    os.chdir(folder)
    storedFiles = os.listdir(folder)
    storedFilesTmp = []

    # skip hidden files
    for i in range(len(storedFiles)):
        if (re.match('^\.', storedFiles[i]) is None):
            storedFilesTmp.append(storedFiles[i])
    storedFiles = storedFilesTmp
    storedFilesTmp = None

    # sort by date
    storedFiles.sort(key=lambda x: os.path.getmtime(x))

    while (len(storedFiles) > rotate):
        oldestFile = folder + '/' + storedFiles[0]
        os.path.exists(oldestFile) and os.remove(oldestFile)
        storedFiles.remove(storedFiles[0])


def sendEmail(podcast, fileName):

    msg = MIMEText(fileName)

    msg['Subject'] = 'New episode of podcast ' + podcast['name'] + ': ' + fileName
    msg['From'] = podcast['email']
    msg['To'] = podcast['email']

    try:
        s = SMTP('localhost')
        s.send_message(msg)
        s.quit()

        return True
    except:
        return False


def isQuiet():
    return (len(sys.argv) > 1 and sys.argv[1] == 'quiet')
