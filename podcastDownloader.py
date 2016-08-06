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

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
logger = logging.getLogger('podcastDownloader')

def processPodcasts(podcasts):

    log('Start')

    shuffle(podcasts)

    for podcast in podcasts:
        processPodcast(podcast)

    log('Finish')


def processPodcast(podcast):

    log('%s: start' % (podcast['name']))

    feed = getFeed(podcast)

    if not feed:
        return

    log('%s: get feed' % (podcast['name']))

    if 'count' not in podcast.keys():
        podcast['count'] = 3

    for item in range(0, podcast['count']):
        processPodcastEpisode(feed, podcast, item)

    log('%s: finish' % (podcast['name']))


def getFeed(podcast):

    tryLimit = 3

    tryNum = 1
    while tryNum <= tryLimit:
        feed = feedparser.parse(podcast['rss'])

        if len(feed.entries) < 1:
            log('%s: get rss %s: %s (of %s) attempt failed' % (podcast['name'], podcast['rss'], str(tryNum), str(tryLimit)))

            if tryNum < tryLimit:
                time.sleep(tryNum * 30)

            tryNum += 1
        else:
            break

    if len(feed.entries) < 1:
        log('%s: unable to get feed by url %s' % (podcast['name'], podcast['rss']), 'error')

        return False

    return feed


def processPodcastEpisode(feed, podcast, item):

    fileUrl = getFileUrlFromFeed(feed, podcast, item)

    if not fileUrl or len(fileUrl) < 24:
        log('%s: unable to get link to file from feed by url %s' % (podcast['name'], podcast['rss']), 'error')

    else:
        fileName = re.search('[0-9a-zA-Z\.\-_]+\.m[p34a]+', fileUrl).group()

        log('%s: get link to file %s' % (podcast['name'], fileName))

        podcast['folder'] = getPodcastFolderPath(podcast['folder'])

        filePath = '%s/%s' % (podcast['folder'], fileName)

        if isEpisodeExists(filePath):
            log('%s: skip, file already exists' % (podcast['name']))

        else:
            downloadEpisode(podcast, fileUrl, filePath)

            removeOldEpisodes(podcast, podcast['count'])

            sendEmail(podcast, fileName)


def getFileUrlFromFeed(feed, podcast, item):

    fileUrl = False

    if type(feed) is feedparser.FeedParserDict and type(feed.entries) is list and len(feed.entries) > 0:

        if len(feed.entries[item].enclosures) and type(feed.entries[item].enclosures[0].href) is str:
            pass
        elif len(feed.entries[item + 1].enclosures) and type(feed.entries[item + 1].enclosures[0].href) is str:
            item = item + 1

        fileUrl = feed.entries[item].enclosures[0].href

    return fileUrl


def getPodcastFolderPath(folder):

    if not os.path.isabs(folder):
        folder = '%s/%s' % (os.path.dirname(os.path.abspath(__file__)), folder)
        folder = os.path.abspath(folder)

    # create folder if not exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def isEpisodeExists(filePath):

    if os.path.isfile(filePath) and os.stat(filePath).st_size == 0:
        os.remove(filePath)

    return os.path.isfile(filePath)


def downloadEpisode(podcast, fileUrl, filePath):

    log('%s: download start' % (podcast['name']))

    if episodeSave(fileUrl, filePath):
        log('%s: download success' % (podcast['name']))
    else:
        log('%s: download failed' % (podcast['name']), 'error')


def episodeSave(fileUrl, filePath):

    # download file
    localFilePath, headers = urllib.request.urlretrieve(fileUrl, filePath)

    # get local file size
    localFile = open(localFilePath)
    localFile.seek(0, os.SEEK_END)
    localFileSize = localFile.tell()
    localFile.close()

    result = localFileSize > 0

    return result


def removeOldEpisodes(podcast, rotate):

    if podcast['count']:

        storedEdisodes = getStoredEpisodes(podcast)

        while (len(storedEdisodes) > rotate):
            if os.path.exists(storedEdisodes[0]):
                os.remove(storedEdisodes[0])

                log('%s: old episode deleted - %s' % (podcast['name'], storedEdisodes[0]))

            storedEdisodes.remove(storedEdisodes[0])


def getStoredEpisodes(podcast):

    storedEdisodes = [os.path.join(podcast['folder'], f) for f in os.listdir(podcast['folder'])]

    # skip hidden files
    storedEdisodesTmp = []
    for i in range(len(storedEdisodes)):
        if (re.match('^\.', storedEdisodes[i]) is None):
            storedEdisodesTmp.append(storedEdisodes[i])

    storedEdisodes = storedEdisodesTmp
    storedEdisodesTmp = None

    # sort by date
    storedEdisodes.sort(key=lambda x: os.path.getmtime(x))

    return storedEdisodes


def sendEmail(podcast, fileName):

    if 'email' in podcast and len(podcast['email']):
        msg = MIMEText(fileName)

        msg['Subject'] = 'New episode of podcast %s: %s' % (podcast['name'], fileName)
        msg['From'] = podcast['email']
        msg['To'] = podcast['email']

        try:
            s = SMTP('localhost')
            s.send_message(msg)
            s.quit()

            log('%s: email to %s sent' % (podcast['name'], podcast['email']))

            return True

        except:
            log('%s: unable to send email' % (podcast['name']), 'warning')

            return False


def isQuiet():

    return (len(sys.argv) > 1 and sys.argv[1] == 'quiet')


def log(message, messageType = 'info'):

    if not isQuiet() or messageType in ['error', 'critical']:

        if messageType == 'debug':
            logger.debug(message)
        elif messageType == 'info':
            logger.info(message)
        elif messageType == 'warning':
            logger.warning(message)
        elif messageType == 'error':
            logger.error(message)
        elif messageType == 'critical':
            logger.critical(message)
