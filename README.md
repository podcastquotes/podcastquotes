podcastquotes
=============
[![Build Status](https://travis-ci.org/podcastquotes/podcastquotes.svg?branch=master)](https://travis-ci.org/podcastquotes/podcastquotes)

A podcast quote transcription, sharing, and rating system inspired by reddit.


Development Install
===================

### Obtain dependencies
```pip install --allow-all-external -r requirements.txt```

### Use podcastquotes settings and site_settings skeleton
```cp ./podcastquotes/settings.py.skel ./podcastquotes/settings.py```
```cp ./podcastquotes/site_settings.py.skel ./podcastquotes/site_settings.py```

### Init database
```./manage.py syncdb```

### Seed database with some things for allauth
```./manage.py init_configuration```

Run App for Development
=======================
```./manage.py runserver```

