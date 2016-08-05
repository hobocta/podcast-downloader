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
        logger.info('%s: start' % (podcast['name']))

    # parse rss (3 attempts)
    tryCount = 1
    tryCounts = 3
    while tryCount <= tryCounts:
        feed = feedparser.parse(podcast['rss'])
        if len(feed.entries) < 1:
            if not isQuiet():
                logger.info('%s: get rss %s: %s (of %s) attempt failed' % (podcast['name'], podcast['rss'], str(tryCount), str(tryCounts)))
            if tryCount < tryCounts:
                time.sleep(tryCount * 30)
            tryCount += 1
        else:
            break

    if len(feed.entries) < 1:
        logger.error('%s: unable to get feed by url %s' % (podcast['name'], podcast['rss']))
        return

    if not isQuiet():
        logger.info('%s: get feed' % (podcast['name']))

    if 'count' not in podcast.keys():
        podcast['count'] = 3

    for item in range(0, podcast['count']):
        processPodcastEpisode(feed, podcast, item)

    if not isQuiet():
        logger.info('%s: finish' % (podcast['name']))

def processPodcastEpisode(feed, podcast, item):

    fileUrl = getFileUrlFromFeed(feed, podcast, item)

    if not fileUrl or len(fileUrl) < 24:
        logger.error('%s: unable to get link to file from feed by url %s' % (podcast['name'], podcast['rss']))
        return

    fileName = re.search('[0-9a-zA-Z\.\-_]+\.m[p34a]+', fileUrl).group()

    if not isQuiet():
        logger.info('%s: get link to file %s' % (podcast['name'], fileName))

    podcast['folder'] = getPodcastFolderPath(podcast['folder'])

    filePath = '%s/%s' % (podcast['folder'], fileName)

    # do we have this file
    if os.path.isfile(filePath) and os.stat(filePath).st_size == 0:
        os.remove(filePath)

    if os.path.isfile(filePath):
        if not isQuiet():
            logger.info('%s: skip, file already exists' % (podcast['name']))
        return

    if not isQuiet():
        logger.info('%s: download start' % (podcast['name']))

    isSaved = podcastSave(fileUrl, filePath)

    if not isSaved:
        logger.error('%s: download failed' % (podcast['name']))
        return

    if not isQuiet():
        logger.info('%s: download success' % (podcast['name']))

    # remove old episodes
    if podcast['count']:
        deleteOldFiles(podcast, podcast['count'])

    # email send
    if 'email' in podcast and len(podcast['email']):
        result = sendEmail(podcast, fileName)
        if not isQuiet():
            if result:
                logger.info('%s: email to %s sent' % (podcast['name'], podcast['email']))
            else:
                logger.warning('%s: unable to send email' % (podcast['name']))


def getPodcastFolderPath(folder):

    if not os.path.isabs(folder):
        folder = '%s/%s' % (os.path.dirname(os.path.abspath(__file__)), folder)
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


def deleteOldFiles(podcast, rotate):

    storedFiles = [os.path.join(podcast['folder'], f) for f in os.listdir(podcast['folder'])]

    # skip hidden files
    storedFilesTmp = []
    for i in range(len(storedFiles)):
        if (re.match('^\.', storedFiles[i]) is None):
            storedFilesTmp.append(storedFiles[i])
    storedFiles = storedFilesTmp
    storedFilesTmp = None

    # sort by date
    storedFiles.sort(key=lambda x: os.path.getmtime(x))

    while (len(storedFiles) > rotate):
        if os.path.exists(storedFiles[0]):
            os.remove(storedFiles[0])

            if not isQuiet():
                logger.info('%s: old episode deleted - %s' % (podcast['name'], storedFiles[0]))

        storedFiles.remove(storedFiles[0])


def sendEmail(podcast, fileName):

    msg = MIMEText(fileName)

    msg['Subject'] = 'New episode of podcast %s: %s' % (podcast['name'], fileName)
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
