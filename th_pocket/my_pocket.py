# -*- coding: utf-8 -*-
# django_th classes
from django_th.services.services import ServicesMgr
from django_th.models import UserService
from django_th.models import ServicesActivated

# django classes
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.log import getLogger

# pocket API
import pocket
from pocket import Pocket

import datetime
import time

logger = getLogger('django_th.trigger_happy')


"""
    handle process with pocket
    put the following in settings.py

    TH_POCKET = {
        'consummer_key': 'abcdefghijklmnopqrstuvwxyz',
    }

"""


class ServicePocket(ServicesMgr):

    def process_data(self, **kwargs):
        """
            get the data from the service
        """
        data = {}
        trigger_id = 0
        if 'trigger_id' in kwargs:
            trigger_id = kwargs['trigger_id']

        date_triggered = ''
        if 'date_triggered' in kwargs:
            date_triggered = kwargs['date_triggered']
        else:
            logger.critical(
                "no date triggered provided for trigger ID %s ", trigger_id)

        token = ''
        if 'token' in kwargs:
            token = kwargs['token']
        else:
            logger.critical(
                "no token provided for trigger ID %s ", trigger_id)

        if token and date_triggered:
            # get the timestamp version of the date time data
            # in data_triggered
            date_triggered = time.mktime(
                datetime.datetime.timetuple(date_triggered))

            pocket_instance = pocket.Pocket(
                settings.TH_POCKET['consummer_key'], token)
            # get the data from the last time the trigger have been started
            data = pocket_instance.get(since=date_triggered)

        return data

    def save_data(self, token, trigger_id, **data):
        """
            let's save the data
        """
        from th_pocket.models import Pocket

        if token and len(data['link']) > 0:
            # get the pocket data of this trigger
            trigger = Pocket.objects.get(trigger_id=trigger_id)

            pocket_instance = pocket.Pocket(
                settings.TH_POCKET['consummer_key'], token)

            title = ''
            title = data['title'] if 'title' in data

            item_id = pocket_instance.add(
                url=data['link'], title=title, tags=(trigger.tag.lower()))

            sentance = str('pocket {} created').format(data['link'])
            logger.debug(sentance)

        else:
            logger.critical(
                "no token provided for trigger ID %s and link %s", trigger_id, data['link'])

    def auth(self, request):
        """
            let's auth the user to the Service
        """
        callbackUrl = 'http://%s%s' % (
            request.get_host(), reverse('pocket_callback'))

        request_token = Pocket.get_request_token(
            consumer_key=settings.TH_POCKET['consummer_key'], redirect_uri=callbackUrl)

        # Save the request token information for later
        request.session['request_token'] = request_token

        # URL to redirect user to, to authorize your app
        auth_url = Pocket.get_auth_url(
            code=request_token, redirect_uri=callbackUrl)

        return auth_url

    def callback(self, request):
        """
            Called from the Service when the user accept to activate it
        """

        try:
            # finally we save the user auth token
            # As we already stored the object ServicesActivated
            # from the UserServiceCreateView now we update the same
            # object to the database so :
            # 1) we get the previous objet
            us = UserService.objects.get(
                user=request.user,
                name=ServicesActivated.objects.get(name='ServicePocket'))
            # 2) then get the token
            access_token = Pocket.get_access_token(
                consumer_key=settings.TH_POCKET['consummer_key'],
                code=request.session['request_token'])

            us.token = access_token
            # 3) and save everything
            us.save()
        except KeyError:
            return '/'

        return 'pocket/callback.html'
