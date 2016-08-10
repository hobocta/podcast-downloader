#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import logging.config
import urllib.request
from smtplib import SMTP
from email.mime.text import MIMEText
import feedparser

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
logger = logging.getLogger('podcast_downloader')


def process_podcasts(config):

    log('Start')

    if check_defaults(config['defaults']):
        for podcast in config['podcasts']:
            if check_podcast_params(podcast):
                podcast = fill_defaults(podcast, config['defaults'])
                process_podcast(podcast)

    log('Finish')


def check_defaults(defaults):

    for param in ['count', 'attempt', 'attempt_delay']:

        if param not in defaults.keys():
            log('Default param %s in not setted' % param, 'error')

            return False

    return True


def fill_defaults(podcast, defaults):

    for param in defaults:
        if param not in podcast.keys() and param in defaults.keys():
            podcast[param] = defaults[param]

    return podcast


def process_podcast(podcast):
    log('%-15s: start' % (podcast['name']), 'debug')

    feed = get_feed(podcast)

    if not feed:
        return

    log('%-15s: get feed' % (podcast['name']), 'debug')

    report_summary = get_report_default()

    for item in range(0, podcast['count']):
        report = process_podcast_episode(feed, podcast, item)
        report_summary = get_report_summ(report_summary, report)

    log('%-15s: skipped: %s, downloaded: %s, deleted: %s, email sent: %s' % (
        podcast['name'],
        report_summary['skip_count'],
        report_summary['download_count'],
        report_summary['remove_count'],
        report_summary['email_count']
    ))

    log('%-15s: finish' % (podcast['name']), 'debug')


def check_podcast_params(podcast):

    for param in ['name', 'rss', 'folder']:

        if param not in podcast.keys():
            log('Podcast param %s in not setted' % param, 'error')

            return False

    return True


def get_report_summ(report_summary, report):
    for key in report_summary:
        report_summary[key] = report_summary[key] + report[key]

    return report_summary


def get_feed(podcast):
    attempt_num = 1

    while attempt_num <= podcast['attempt']:
        feed = feedparser.parse(podcast['rss'])

        if len(feed.entries) < 1:
            log('%-15s: get rss %s: %s (of %s) attempt failed' % (
                podcast['name'],
                podcast['rss'],
                str(attempt_num),
                str(podcast['attempt'])
            ), 'warning')

            if attempt_num < podcast['attempt']:
                time.sleep(podcast['attempt_delay'])

            attempt_num += 1
        else:
            break

    try:
        if len(feed.entries):
            return feed
        else:
            log('%-15s: unable to get feed by url %s ' % (podcast['name'], podcast['rss']), 'error')

    except NameError:
        log('NameError: variable "feed" does not exist', 'error')

    return False


def process_podcast_episode(feed, podcast, item):

    report = get_report_default()

    file_url = get_file_url_from_feed(feed, item)

    if not file_url or len(file_url) < 24:
        log('%-15s: unable to get link to file from feed by url %s ' % (podcast['name'], podcast['rss']), 'error')

    else:
        file_name = re.search('[0-9a-zA-Z.\-_]+\.m[p34a]+', file_url).group()

        log('%-15s: get link to file %s' % (podcast['name'], file_name), 'debug')

        podcast['folder'] = get_podcast_folder_path(podcast['folder'])

        file_path = os.path.join(podcast['folder'], file_name)

        if is_episode_exists(file_path):
            log('%-15s: skip, file already exists' % (podcast['name']), 'debug')
            report['skip_count'] += 1

        else:
            if download_episode(podcast, file_url, file_path):
                report['download_count'] += 1

            if send_email(podcast, file_name):
                report['email_count'] += 1

        remove_count = remove_old_episodes(podcast, podcast['count'])
        report['remove_count'] += remove_count

    return report


def get_report_default():
    return {'skip_count': 0, 'download_count': 0, 'remove_count': 0, 'email_count': 0}


def get_file_url_from_feed(feed, item):

    file_url = False

    if type(feed) is feedparser.FeedParserDict and type(feed.entries) is list and len(feed.entries) > 0:

        if len(feed.entries[item].enclosures) and type(feed.entries[item].enclosures[0].href) is str:
            pass
        elif len(feed.entries[item + 1].enclosures) and type(feed.entries[item + 1].enclosures[0].href) is str:
            item += 1

        file_url = feed.entries[item].enclosures[0].href

    return file_url


def get_podcast_folder_path(folder):

    if not os.path.isabs(folder):
        folder = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), folder))

    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def is_episode_exists(file_path):

    if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
        os.remove(file_path)

    return os.path.isfile(file_path)


def download_episode(podcast, file_url, file_path):

    log('%-15s: download start' % (podcast['name']), 'debug')

    if episode_save(file_url, file_path):
        log('%-15s: download success' % (podcast['name']), 'debug')

        return True
    else:
        log('%-15s: download failed' % (podcast['name']), 'error')

        return False


def episode_save(file_url, file_path):

    # download file
    local_file_path, headers = urllib.request.urlretrieve(file_url, file_path)

    # get local file size
    local_file = open(local_file_path)
    local_file.seek(0, os.SEEK_END)
    local_file_size = local_file.tell()
    local_file.close()

    return local_file_size > 0


def remove_old_episodes(podcast, rotate):

    remove_count = 0

    if podcast['count']:

        stored_edisodes = get_stored_episodes(podcast)

        while len(stored_edisodes) > rotate:
            if os.path.exists(stored_edisodes[0]):
                os.remove(stored_edisodes[0])

                remove_count += 1

                log('%-15s: old episode deleted - %s' % (podcast['name'], stored_edisodes[0]), 'debug')

            stored_edisodes.remove(stored_edisodes[0])

    return remove_count


def get_stored_episodes(podcast):

    stored_edisodes = [os.path.join(podcast['folder'], f) for f in os.listdir(podcast['folder'])]

    # skip hidden files
    stored_edisodes_tmp = []
    for i in range(len(stored_edisodes)):
        if re.match('^\.', stored_edisodes[i]) is None:
            stored_edisodes_tmp.append(stored_edisodes[i])

    stored_edisodes = stored_edisodes_tmp

    # sort by date
    stored_edisodes.sort(key=lambda x: os.path.getmtime(x))

    return stored_edisodes


def send_email(podcast, file_name):

    if 'email' in podcast and len(podcast['email']):
        msg = MIMEText(file_name)

        msg['Subject'] = 'New episode of podcast %s: %s' % (podcast['name'], file_name)
        msg['From'] = podcast['email']
        msg['To'] = podcast['email']

        try:
            s = SMTP('localhost')
            s.send_message(msg)
            s.quit()

            log('%-15s: email to %s sent' % (podcast['name'], podcast['email']), 'debug')

            return True

        except ConnectionRefusedError:
            log('%-15s: unable to send email' % (podcast['name']), 'warning')

            return False


def is_quiet():
    return len(sys.argv) > 1 and sys.argv[1] == 'quiet'


def is_debug():
    return len(sys.argv) > 1 and sys.argv[1] == 'debug'


def log(message, message_type='info'):

    if not is_quiet() or message_type in ['error', 'critical']:

        if message_type == 'debug' and is_debug():
            logger.debug(message)
        elif message_type == 'info':
            logger.info(message)
        elif message_type == 'warning':
            logger.warning(message)
        elif message_type == 'error':
            logger.error(message)
        elif message_type == 'critical':
            logger.critical(message)
