#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    'defaults': {
        'count': 3,
        'attempts': 5,
        'attempt_delay': 60,
        'email': 'contact@site-home.ru',
        # Get your key there https://console.developers.google.com/apis/credentials
        # 'google_drive_api_key': 'put-your-key-here'
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
            'rss': 'https://rss.simplecast.com/podcasts/4121/rss',
            'folder': '../podcasts/inf100',
        },
        {
            'name': 'DevZen',
            'rss': 'http://devzen.ru/feed/',
            'folder': '../podcasts/devzen',
        },
        {
            'name': 'Web standards',
            'rss': 'http://feeds.soundcloud.com/users/soundcloud:users:202737209/sounds.rss',
            'folder': '../podcasts/web-standards',
        },
        {
            'name': 'Five min php',
            'rss': 'http://feeds.soundcloud.com/users/soundcloud:users:153519653/sounds.rss',
            'folder': '../podcasts/fiveminphp',
        },
        {
            'name': 'Ostretsov',
            'rss': 'http://podcast.ostretsov.ru/feed/rss.xml',
            'folder': '../podcasts/ostretsov',
        },
    ]
}
