


podcastquotes
=============
[![Build Status](https://travis-ci.org/podcastquotes/podcastquotes.svg?branch=master)](https://travis-ci.org/podcastquotes/podcastquotes)
[![Coverage Status](https://coveralls.io/repos/podcastquotes/podcastquotes/badge.png?branch=master)](https://coveralls.io/r/podcastquotes/podcastquotes?branch=master)

A podcast transcription, highlight sharing, and rating system inspired by reddit.  Django & Python 2 


Development Install
===================

### Obtain dependencies
```pip install -r requirements.txt```

Sometimes this external version of argparse sneaks in, I don't know what it is but if your version of pip is very new then you need to allow external dependencies using ```--allow-all-external```.  It's a mess.

### Use podcastquotes settings and site_settings skeleton
```cp ./podcastquotes/settings.py.skel ./podcastquotes/settings.py```
```cp ./podcastquotes/site_settings.py.skel ./podcastquotes/site_settings.py```

### Init database
```./manage.py syncdb```  
```./manage.py migrate```

### Seed database with some things for allauth
```./manage.py init_configuration```

Run App for Development
=======================
```./manage.py runserver```


Database tasks
===============
```./manage.py update_rss_feeds``` - Poll all rss feeds  
```./manage.py rank_quotes``` - Recalculate 'hot' score for quotes  

Dev Tricks
==========

## Aliases

```source set_aliases```

* autotest
    * Automatically watches files in the project and reruns tests when they change (using py.test)
* manage
    * shortcut for manage.py
* masks ```*.pyc``` files when using ```ls```

## Focus on particular test
```autotest -k test_name```
