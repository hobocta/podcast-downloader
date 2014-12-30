podcast-downloader
==================

**Скрипт на python 3, который скачивает свежие подкасты из указанных RSS лент**

--

Для работы требуется установленный пакет [feedparser](https://pypi.python.org/pypi/feedparser)

--

На вход принимает список подкастов в следующем формате:

```
download = [
    {
        "name": "Радио-Т",
        "rss_url": "http://feeds.rucast.net/radio-t",
        "folder": "/home/btsync/podcasts/radio-t",
        "rotate": 3,
        "email": "contact@site-home.ru",
    },
]
```

* name — имя подкаста
* rss_url — rss лента из которой можно взять mp3'шки
* folder — полный путь к папке куда будем складывать файлы, без слеша вконце, для каждого подкаста обязательно нужно завести отдельную папку (создать вручную), чтобы корректно отрабатывало удаление старых подкастов, когда количество файлов в папке превышает цифру указанную в параметре rotate
* rotate — сколько крайних подкастов хранить
* email — куда отправить уведомление о новом подкасте, не обязательно к заполнения

--

При запуске с ключом hide сообщения на экран выводиться не будут.

--

Запускать на linux можно через crontab, например так:
```
*/10 * * * * python3 /home/python/podcast-downloader/run.py hide
```

Для запуска из под windows имеется файл run.cmd.

--

Выполнение скрипта в консоли выглядит примерно так:
![Скриншот bash](https://dl.dropboxusercontent.com/u/15126083/ShareX/2014/12/2014-12-30_21-24-43.png)

--

Уведомление, приходящее на почту, выглядит так:
![Скриншот письма](https://dl.dropboxusercontent.com/u/15126083/ShareX/2014/12/2014-12-30_21-25-52.png)
