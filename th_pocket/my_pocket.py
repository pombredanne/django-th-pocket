# -*- coding: utf-8 -*-
# django_th classes
from django_th.services.services import ServicesMgr
from django_th.models import UserService, ServicesActivated, TriggerService
# django classes
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.log import getLogger

# pocket API
import pocket
from pocket import Pocket

import datetime
import time
import json
"""
    handle process with pocket
    put the following in settings.py

    TH_POCKET = {
        'consummer_key': 'abcdefghijklmnopqrstuvwxyz',
    }

"""

logger = getLogger('django_th.trigger_happy')


class ServicePocket(ServicesMgr):

    def process_data(self, token, trigger_id, date_triggered):
        """
            get the data from the service
        """
        datas = list()

        date_triggered = int(time.mktime(datetime.datetime.timetuple(date_triggered)))

        if token is not None:

            pocket_instance = pocket.Pocket(settings.TH_POCKET['consummer_key'], token)

            # get the data from the last time the trigger have been started
            # timestamp form
            pockets = pocket_instance.get(since=date_triggered)

            if len(pockets[0]['list']) > 0:
                for pocket in pockets[0]['list'].values():

                    datas.append({'tag': '',
                        'link': pocket['resolved_url'],
                        'title': pocket['resolved_title'],
                        'tweet_id': 0,
                        'trigger': trigger})

        return datas

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
            title = (data['title'] if 'title' in data else '')

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
