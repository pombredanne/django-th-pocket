# -*- coding: utf-8 -*-

from django.db import models
from django_th.models.services import Services


class Pocket(Services):

    tag = models.CharField(max_length=80, blank=True)
    url = models.URLField(max_length=255)
    title = models.CharField(max_length=80, blank=True)
    tweet_id = models.CharField(max_length=80, blank=True)
    trigger = models.ForeignKey('TriggerService')

    class Meta:
        app_label = 'django_th'

    def __unicode__(self):
        return "%s" % (self.title)

    def show(self):
        return "My Pocket %s" % (self.title)
