#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    'defaults': {
        'count': 3,
        'attempts': 5,
        'attempt_delay': 60,
        # 'email': 'test@example.com',
        # Get your key there https://console.developers.google.com/apis/credentials
        # 'google_drive_api_key': 'put-your-key-here'
    },
    'podcasts': [
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
            'rss': 'https://cloud.mave.digital/32782',
            'folder': '../podcasts/fiveminphp',
        },
    ]
}
