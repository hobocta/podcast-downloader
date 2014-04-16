podcast-downloader
==================

**Скрипт на python 3, который скачивает свежие подкасты из указанных RSS лент**

--

На вход принимает список подкастов в следующем формате:

```
download = [
    {
        "name": "Радио-Т",
        "rss_url": "http://feeds.rucast.net/radio-t",
        "folder": "~/podcasts/radio-t",
        "rotate": 5,
    },
]
```

* name — имя подкаста
* rss_url — rss лента из которой можно взять mp3'шки
* folder — полный путь к папке куда будем складывать файлы, без слеша вконце
* rotate — сколько крайних подкастов хранить, желательно больше нуля :)

--

При запуске с ключём hide сообщения на экран выводиться не будут.

--

Запускать на линуксе можно через crontab, например так:
```
*/5 * * * * /usr/local/bin/python3.3 ~/podcast-downloader/script.py hide 2>&1 >/dev/null
```

Для запуска из под windows имеется файл run.cmd.

--

Выполнение скрипта в консоли выглядит так — http://i.imgur.com/rlv84uj.png
