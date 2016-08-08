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
from smtplib import SMTP
from email.mime.text import MIMEText
import feedparser

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
logger = logging.getLogger('podcastDownloader')

def processPodcasts(podcasts, defaults):

    log('Start')

    if checkDefaults(defaults):
        for podcast in podcasts:
            if checkPodcastParams(podcast):
                podcast = fillDefaults(podcast, defaults)
                processPodcast(podcast)

    log('Finish')


def checkDefaults(defaults):

    for param in ['count', 'attempt', 'attemptDelay']:

        if param not in defaults.keys():
            log('Default param %s in not setted' % param, 'error')

            return False

    return True


def fillDefaults(podcast, defaults):

    for param in defaults:
        if param not in podcast.keys() and param in defaults.keys():
            podcast[param] = defaults[param]

    return podcast


def processPodcast(podcast):
    log('%-15s: start' % (podcast['name']), 'dubug')

    feed = getFeed(podcast)

    if not feed:
        return

    log('%-15s: get feed' % (podcast['name']), 'dubug')

    reportSummary = getReportDefault()

    for item in range(0, podcast['count']):
        report = processPodcastEpisode(feed, podcast, item)
        reportSummary = getReportSumm(reportSummary, report)

    log('%-15s: skipped: %s, downloaded: %s, deleted: %s, email sent: %s' % (
        podcast['name'],
        reportSummary['skipCount'],
        reportSummary['downloadCount'],
        reportSummary['removeCount'],
        reportSummary['emailCount']
    ))

    log('%-15s: finish' % (podcast['name']), 'dubug')


def checkPodcastParams(podcast):

    for param in ['name', 'rss', 'folder']:

        if param not in podcast.keys():
            log('Podcast param %s in not setted' % param, 'error')

            return False

    return True


def getReportSumm(reportSummary, report):
    for key in reportSummary:
        reportSummary[key] = reportSummary[key] + report[key]

    return reportSummary


def getFeed(podcast):
    attemptNum = 1

    while attemptNum <= podcast['attempt']:
        feed = feedparser.parse(podcast['rss'])

        if len(feed.entries) < 1:
            log('%-15s: get rss %s: %s (of %s) attempt failed' % (podcast['name'], podcast['rss'], str(attemptNum), str(podcast['attempt'])), 'warning')

            if attemptNum < podcast['attempt']:
                time.sleep(attemptNum * podcat['attemptDelay'])

            attemptNum += 1
        else:
            break

    if len(feed.entries) < 1:
        log('%-15s: unable to get feed by url %s ' % (podcast['name'], podcast['rss']), 'error')

        return False

    return feed


def processPodcastEpisode(feed, podcast, item):

    report = getReportDefault()

    fileUrl = getFileUrlFromFeed(feed, podcast, item)

    if not fileUrl or len(fileUrl) < 24:
        log('%-15s: unable to get link to file from feed by url %s ' % (podcast['name'], podcast['rss']), 'error')

    else:
        fileName = re.search('[0-9a-zA-Z\.\-_]+\.m[p34a]+', fileUrl).group()

        log('%-15s: get link to file %s' % (podcast['name'], fileName), 'debug')

        podcast['folder'] = getPodcastFolderPath(podcast['folder'])

        filePath = os.path.join(podcast['folder'], fileName)

        if isEpisodeExists(filePath):
            log('%-15s: skip, file already exists' % (podcast['name']), 'debug')
            report['skipCount'] = report['skipCount'] + 1

        else:
            if downloadEpisode(podcast, fileUrl, filePath):
                report['downloadCount'] = report['downloadCount'] + 1

            if sendEmail(podcast, fileName):
                report['emailCount'] = report['emailCount'] + 1

        removeCount = removeOldEpisodes(podcast, podcast['count'])
        report['removeCount'] = report['removeCount'] + removeCount


    return report


def getReportDefault():
    return {'skipCount': 0, 'downloadCount': 0, 'removeCount': 0, 'emailCount': 0}

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
        folder = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), folder))

    # create folder if not exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def isEpisodeExists(filePath):

    if os.path.isfile(filePath) and os.stat(filePath).st_size == 0:
        os.remove(filePath)

    return os.path.isfile(filePath)


def downloadEpisode(podcast, fileUrl, filePath):

    log('%-15s: download start' % (podcast['name']), 'debug')

    if episodeSave(fileUrl, filePath):
        log('%-15s: download success' % (podcast['name']), 'debug')

        return True
    else:
        log('%-15s: download failed' % (podcast['name']), 'error')

        return False


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

    removeCount = 0

    if podcast['count']:

        storedEdisodes = getStoredEpisodes(podcast)

        while (len(storedEdisodes) > rotate):
            if os.path.exists(storedEdisodes[0]):
                os.remove(storedEdisodes[0])

                removeCount = removeCount + 1

                log('%-15s: old episode deleted - %s' % (podcast['name'], storedEdisodes[0]), 'debug')

            storedEdisodes.remove(storedEdisodes[0])

    return removeCount


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

            log('%-15s: email to %s sent' % (podcast['name'], podcast['email']), 'debug')

            return True

        except:
            log('%-15s: unable to send email' % (podcast['name']), 'warning')

            return False


def isQuiet():
    return (len(sys.argv) > 1 and sys.argv[1] == 'quiet')


def isDebug():
    return (len(sys.argv) > 1 and sys.argv[1] == 'debug')


def log(message, messageType = 'info'):

    if not isQuiet() or messageType in ['error', 'critical']:

        if messageType == 'debug' and isDebug():
            logger.debug(message)
        elif messageType == 'info':
            logger.info(message)
        elif messageType == 'warning':
            logger.warning(message)
        elif messageType == 'error':
            logger.error(message)
        elif messageType == 'critical':
            logger.critical(message)
