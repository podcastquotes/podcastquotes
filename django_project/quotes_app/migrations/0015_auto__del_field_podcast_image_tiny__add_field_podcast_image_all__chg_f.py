# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Podcast.image_tiny'
        db.delete_column(u'quotes_app_podcast', 'image_tiny')

        # Adding field 'Podcast.image_all'
        db.add_column(u'quotes_app_podcast', 'image_all',
                      self.gf('stdimage.fields.StdImageField')(default=1234, max_length=100, blank=True),
                      keep_default=False)


        # Changing field 'Podcast.image'
        db.alter_column(u'quotes_app_podcast', 'image', self.gf('stdimage.fields.StdImageField')(max_length=100))

        # Changing field 'Podcast.image_small'
        db.alter_column(u'quotes_app_podcast', 'image_small', self.gf('stdimage.fields.StdImageField')(max_length=100))

    def backwards(self, orm):
        # Adding field 'Podcast.image_tiny'
        db.add_column(u'quotes_app_podcast', 'image_tiny',
                      self.gf('django_resized.forms.ResizedImageField')(default=1234, max_length=100, max_height=100, max_width=100, blank=True),
                      keep_default=False)

        # Deleting field 'Podcast.image_all'
        db.delete_column(u'quotes_app_podcast', 'image_all')


        # Changing field 'Podcast.image'
        db.alter_column(u'quotes_app_podcast', 'image', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Changing field 'Podcast.image_small'
        db.alter_column(u'quotes_app_podcast', 'image_small', self.gf('django_resized.forms.ResizedImageField')(max_length=100, max_height=250, max_width=250))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quotes_app.episode': {
            'Meta': {'ordering': "['-publication_date']", 'object_name': 'Episode'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'episode_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quotes_app.Podcast']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'support_recipient': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'support_recipient_about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'support_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'quotes_app.podcast': {
            'Meta': {'object_name': 'Podcast'},
            'alphabetical_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'google_plus_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'blank': 'True'}),
            'image_all': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'blank': 'True'}),
            'image_small': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'blank': 'True'}),
            'instagram_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'is_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'managed_by_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderators': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'reddit_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'rss_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'support_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'tumblr_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'twitter_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'quotes_app.quote': {
            'Meta': {'object_name': 'Quote'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quotes_app.Episode']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_full_episode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rank_score': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'submitted_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_quote_begins': ('django.db.models.fields.IntegerField', [], {}),
            'time_quote_ends': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'quotes_app.userprofile': {
            'Meta': {'ordering': "['user']", 'object_name': 'UserProfile'},
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'google_plus_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'instagram_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'reddit_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'support_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'twitter_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'quotes_app.vote': {
            'Meta': {'object_name': 'Vote'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quote': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quotes_app.Quote']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vote_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['quotes_app']