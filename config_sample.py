#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    'defaults': {
        'count': 3,
        'attempts': 5,
        'attempt_delay': 60,
        'email': 'contact@site-home.ru'
    },
    'podcasts': [
        {
            'name': 'The Big Podcast',
            'rss': 'http://bigpodcast.ru/rss',
            'folder': '../podcasts/tbp',
        },
        {
            'name': 'Radio-T',
            'rss': 'http://feeds.rucast.net/radio-t',
            'folder': '../podcasts/radio-t',
        },
        {
            'name': 'Pirate Radio-T',
            'rss': 'http://feeds.feedburner.com/pirate-radio-t',
            'folder': '../podcasts/pirate',
        },
        {
            'name': 'RubyNoName',
            'rss': 'http://feeds.feedburner.com/rubynoname-standalone',
            'folder': '../podcasts/rubynoname',
        },
        {
            'name': 'Razbor Poletov',
            'rss': 'http://feeds.feedburner.com/razbor-podcast',
            'folder': '../podcasts/razbor-poletov',
        },
        {
            'name': 'Umputun',
            'rss': 'http://feeds.rucast.net/Umputun',
            'folder': '../podcasts/umputun',
        },
        {
            'name': 'AppleInsider',
            'rss': 'http://ai.libsyn.com/rss',
            'folder': '../podcasts/appleinsider',
        },
        {
            'name': 'Infa 100%',
            'rss': 'http://feeds.feedburner.com/inf100/WmpG',
            'folder': '../podcasts/inf100',
        },
        {
           'name': 'DevZen',
           'rss': 'http://devzen.ru/feed/',
           'folder': '../podcasts/devzen',
           'email': 'contact@site-home.ru',
        },
        {
           'name': 'Web standards',
           'rss': 'http://feeds.soundcloud.com/users/soundcloud:users:202737209/sounds.rss',
           'folder': '../podcasts/web-standards',
           'email': 'contact@site-home.ru',
        },
    ]
}
