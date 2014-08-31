# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from th_pocket.models import Pocket
from django_th.models import TriggerService, UserService, ServicesActivated
from th_pocket.forms import PocketProviderForm, PocketConsumerForm


class PocketTest(TestCase):

    """
        PocketTest Model
    """
    def setUp(self):
        try:
            self.user = User.objects.get(username='john')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='john', email='john@doe.info', password='doe')

    def create_triggerservice(self, date_created="20130610",
                              description="My first Service", status=True):
        user = self.user
        service_provider = ServicesActivated.objects.create(
            name='ServicePocket', status=True,
            auth_required=False, description='Service Pocket')
        service_consumer = ServicesActivated.objects.create(
            name='ServiceEvernote', status=True,
            auth_required=True, description='Service Evernote')
        provider = UserService.objects.create(user=user,
                                              token="AZERTY1234",
                                              name=service_provider)
        consumer = UserService.objects.create(user=user,
                                              token="AZERTY1234",
                                              name=service_consumer)
        return TriggerService.objects.create(provider=provider,
                                             consumer=consumer,
                                             user=user,
                                             date_created=date_created,
                                             description=description,
                                             status=status)

    def create_pocket(self):
        trigger = self.create_triggerservice()
        tag = 'test'
        url = 'http://foobar.com/somewhere/in/the/rainbow'
        title = 'foobar'
        tweet_id = ''
        status = True
        return Pocket.objects.create(tag=tag, url=url, title=title,
                                     tweet_id=tweet_id, trigger=trigger,
                                     status=status)

    def test_pocket(self):
        p = self.create_pocket()
        self.assertTrue(isinstance(p, Pocket))
        self.assertEqual(p.show(), "My Pocket %s" % (p.title))

    """
        Form
    """
    def test_valid_provider_form(self):
        p = self.create_pocket()
        data = {'tag': p.tag}
        form = PocketProviderForm(data=data)
        self.assertTrue(form.is_valid())

    def test_valid_consumer_form(self):
        p = self.create_pocket()
        data = {'tag': p.tag}
        form = PocketConsumerForm(data=data)
        self.assertTrue(form.is_valid())
