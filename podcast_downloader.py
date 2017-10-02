#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging.config
import os
import re
import sys
import time
import urllib.request
from email.mime.text import MIMEText
from http.client import RemoteDisconnected
from smtplib import SMTP
from urllib.error import HTTPError
from urllib.error import URLError

import feedparser
from typing import Type


class PodcastDownloader:
    def __init__(self, config: dict):
        logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
        self.logger = logging.getLogger('podcast_downloader')

        self.config = config

    def process_podcasts(self) -> bool:
        self.log('Start')

        if self.check_defaults(self.config['defaults']):
            for podcast in self.config['podcasts']:
                if self.check_podcast_params(podcast):
                    podcast = self.fill_defaults(podcast, self.config['defaults'])
                    self.process_podcast(podcast)

        self.log('Finish')

        return True

    def check_defaults(self, defaults: dict) -> bool:
        for param in ['count', 'attempts', 'attempt_delay']:

            if param not in defaults.keys():
                self.log('Default param %s in not setted' % param, 'error')

                return False

        return True

    @staticmethod
    def fill_defaults(podcast: dict, defaults: dict) -> dict:
        for param in defaults:
            if param not in podcast.keys() and param in defaults.keys():
                podcast[param] = defaults[param]

        return podcast

    def process_podcast(self, podcast: dict) -> bool:
        self.log('%-15s: start' % (podcast['name']), 'debug')

        feed = self.get_feed(podcast)

        if not hasattr(feed, 'entries'):
            return False

        self.log('%-15s: get feed' % (podcast['name']), 'debug')

        report_summary = self.get_report_default()

        for item in range(0, podcast['count']):
            report = self.process_podcast_episode(feed, podcast, item)
            report_summary = self.get_report_summ(report_summary, report)

        self.log('%-15s: skipped: %s, downloaded: %s, deleted: %s, email sent: %s' % (
            podcast['name'],
            report_summary['skip_count'],
            report_summary['download_count'],
            report_summary['remove_count'],
            report_summary['email_count']
        ))

        self.log('%-15s: finish' % (podcast['name']), 'debug')

        return True

    def check_podcast_params(self, podcast: dict) -> bool:
        for param in ['name', 'rss', 'folder']:

            if param not in podcast.keys():
                self.log('Podcast param %s in not setted' % param, 'error')

                return False

        return True

    @staticmethod
    def get_report_summ(report_summary: dict, report: dict) -> dict:
        for key in report_summary:
            report_summary[key] = report_summary[key] + report[key]

        return report_summary

    def get_feed(self, podcast: dict) -> Type[feedparser.FeedParserDict]:
        attempt_num = 1

        feed = feedparser.FeedParserDict

        while attempt_num <= podcast['attempts']:
            feed = feedparser.parse(podcast['rss'])

            if len(feed.entries) < 1:
                self.log('%-15s: get rss %s: %s (of %s) attempt failed, http code: %s' % (
                    podcast['name'],
                    podcast['rss'],
                    str(attempt_num),
                    str(podcast['attempts']),
                    feed.status if 'status' in feed else 'none'
                ), 'warning')

                if attempt_num < podcast['attempts']:
                    time.sleep(podcast['attempt_delay'])

                attempt_num += 1
            else:
                break

        try:
            if len(feed.entries):
                return feed
            else:
                self.log('%-15s: unable to get feed by url %s with %s attempts per %s seconds' % (
                    podcast['name'],
                    podcast['rss'],
                    podcast['attempts'],
                    podcast['attempt_delay']
                ), 'error')
                self.log(feed, 'error')

        except NameError:
            self.log('NameError: variable "feed" does not exist', 'error')

        return feedparser.FeedParserDict

    def process_podcast_episode(self, feed: Type[feedparser.FeedParserDict], podcast: dict, item: int) -> dict:
        report = self.get_report_default()

        file_url = self.get_file_url_from_feed(feed, item)

        if not file_url or len(file_url) < 24:
            self.log(
                '%-15s: unable to get link to file from feed by url %s ' % (podcast['name'], podcast['rss']),
                'error'
            )

        else:
            file_name = self.get_file_name(file_url)

            if len(file_name) < 1:
                self.log('%-15s: unable to get file name form link %s' % (podcast['name'], file_url), 'error')
                report['skip_count'] += 1
            else:
                self.log('%-15s: get link to file %s' % (podcast['name'], file_name), 'debug')

                podcast['folder'] = self.get_podcast_folder_path(podcast['folder'])

                file_path = os.path.join(podcast['folder'], file_name)

                if self.is_episode_exists(file_path):
                    self.log('%-15s: skip, file already exists' % (podcast['name']), 'debug')
                    report['skip_count'] += 1

                else:
                    if self.download_episode(podcast, file_url, file_path):
                        report['download_count'] += 1

                        if self.send_email(podcast, file_name):
                            report['email_count'] += 1

                remove_count = self.remove_old_episodes(podcast, podcast['count'])
                report['remove_count'] += remove_count

        return report

    def get_file_name(self, file_url: str) -> str:
        file_name = ''

        file_name_re = self.get_file_name_re(file_url)

        if file_name_re is None:
            try:
                file_url = self.get_redirect_url(file_url)
                file_name_re = self.get_file_name_re(file_url)
            except RemoteDisconnected as e:
                self.log('Unable to get redirect url, except: %s' % e, 'error')
                return ''

        if file_name_re is not None:
            file_name = file_name_re.group()

        return file_name

    @staticmethod
    def get_file_name_re(file_url: str) -> re.search:
        return re.search('[0-9a-zA-Z.\-_]+\.m[p34a]+', file_url)

    @staticmethod
    def get_redirect_url(file_url: str) -> str:
        return urllib.request.urlopen(file_url).geturl()

    @staticmethod
    def get_report_default() -> dict:
        return {'skip_count': 0, 'download_count': 0, 'remove_count': 0, 'email_count': 0}

    @staticmethod
    def get_file_url_from_feed(feed: Type[feedparser.FeedParserDict], start_item: int) -> str:
        file_url = False

        if type(feed) is feedparser.FeedParserDict and type(feed.entries) is list and len(feed.entries) >= start_item:

            for item in range(start_item, len(feed.entries)):
                if len(feed.entries[item].enclosures) and type(feed.entries[item].enclosures[0].href) is str:
                    file_url = feed.entries[item].enclosures[0].href
                    break

        return file_url

    @staticmethod
    def get_podcast_folder_path(folder: str) -> str:
        if not os.path.isabs(folder):
            folder = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), folder))

        if not os.path.exists(folder):
            os.makedirs(folder)

        return folder

    @staticmethod
    def is_episode_exists(file_path: str) -> bool:
        if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
            os.remove(file_path)

        return os.path.isfile(file_path)

    def download_episode(self, podcast: dict, file_url: str, file_path: str) -> bool:
        self.log('%-15s: download start' % (podcast['name']), 'debug')

        if self.episode_save(file_url, file_path):
            self.log('%-15s: download success' % (podcast['name']), 'debug')

            return True
        else:
            self.log('%-15s: download failed' % (podcast['name']), 'error')

            return False

    def episode_save(self, file_url: str, file_path: str) -> bool:
        # download file
        try:
            local_file_path, headers = urllib.request.urlretrieve(file_url, file_path)

        except HTTPError as e:
            self.log('Unable to download file by url: %s, except: %s' % (file_url, e), 'error')

            return False

        except URLError as e:
            self.log('Unable to download file by url: %s, except: %s' % (file_url, e), 'error')

            return False

        # get local file size
        local_file = open(local_file_path)
        local_file.seek(0, os.SEEK_END)
        local_file_size = local_file.tell()
        local_file.close()

        return local_file_size > 0

    def remove_old_episodes(self, podcast: dict, rotate: int) -> int:
        remove_count = 0

        if podcast['count']:

            stored_edisodes = self.get_stored_episodes(podcast)

            while len(stored_edisodes) > rotate:
                if os.path.exists(stored_edisodes[0]):
                    os.remove(stored_edisodes[0])

                    remove_count += 1

                    self.log('%-15s: old episode deleted - %s' % (podcast['name'], stored_edisodes[0]), 'debug')

                stored_edisodes.remove(stored_edisodes[0])

        return remove_count

    @staticmethod
    def get_stored_episodes(podcast: dict) -> list:
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

    def send_email(self, podcast: dict, file_name: str) -> bool:
        if 'email' in podcast and len(podcast['email']):
            msg = MIMEText(file_name)

            msg['Subject'] = '%s: new episode - %s' % (podcast['name'], file_name)
            msg['From'] = podcast['email']
            msg['To'] = podcast['email']

            try:
                s = SMTP('localhost')
                s.send_message(msg)
                s.quit()

                self.log('%-15s: email to %s sent' % (podcast['name'], podcast['email']), 'debug')

                return True

            except ConnectionRefusedError:
                self.log('%-15s: unable to send email' % (podcast['name']), 'warning')

                return False

    @staticmethod
    def is_quiet() -> bool:
        return len(sys.argv) > 1 and sys.argv[1] == 'quiet'

    @staticmethod
    def is_debug() -> bool:
        return len(sys.argv) > 1 and sys.argv[1] == 'debug'

    @staticmethod
    def is_warning() -> bool:
        return len(sys.argv) > 1 and sys.argv[1] == 'warning'

    def log(self, message: str, message_type: str = 'info'):
        if message_type in self.get_log_allowed_types():

            if message_type == 'debug':
                self.logger.debug(message)
            elif message_type == 'info':
                self.logger.info(message)
            elif message_type == 'warning':
                self.logger.warning(message)
            elif message_type == 'error':
                self.logger.error(message)
            elif message_type == 'critical':
                self.logger.critical(message)

    def get_log_allowed_types(self) -> list:
        if self.is_quiet():
            return ['critical', 'error']
        elif self.is_warning():
            return ['critical', 'error', 'warning']
        elif self.is_debug():
            return ['critical', 'error', 'warning', 'info', 'debug']
        else:
            return ['critical', 'error', 'warning', 'info']
