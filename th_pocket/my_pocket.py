# -*- coding: utf-8 -*-
import datetime
import time
import arrow

# pocket API
import pocket
from pocket import Pocket

# django classes
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.log import getLogger

# django_th classes
from django_th.services.services import ServicesMgr
from django_th.models import UserService, ServicesActivated

"""
    handle process with pocket
    put the following in settings.py

    TH_POCKET = {
        'consumer_key': 'abcdefghijklmnopqrstuvwxyz',
    }

    TH_SERVICES = (
        ...
        'th_pocket.my_pocket.ServicePocket',
        ...
    )

"""

logger = getLogger('django_th.trigger_happy')


class ServicePocket(ServicesMgr):

    def process_data(self, token, trigger_id, date_triggered):
        """
            get the data from the service
            as the pocket service does not have any date
            in its API linked to the note,
            add the triggered date to the dict data
            thus the service will be triggered when data will be found
        """
        datas = list()
        # pocket uses a timestamp date format
        since = int(
            time.mktime(datetime.datetime.timetuple(date_triggered)))

        pocket_instance = ''

        if token is not None:

            pocket_instance = Pocket(
                settings.TH_POCKET['consumer_key'], token)

            # get the data from the last time the trigger have been started
            # timestamp form
            pockets = pocket_instance.get(since=since, state="unread")

            if pockets is not None and len(pockets[0]['list']) > 0:
                for pocket in pockets[0]['list'].values():
                    content = (pocket['excerpt'] if pocket['excerpt'] else pocket['given_title'])
                    datas.append({'my_date': str(arrow.get(str(date_triggered), 'YYYY-MM-DD HH:mm:ss').to(settings.TIME_ZONE)),
                                  'tag': '',
                                  'link': pocket['given_url'],
                                  'title': pocket['given_title'],
                                  'content': content,
                                  'tweet_id': 0})
        return datas

    def save_data(self, token, trigger_id, **data):
        """
            let's save the data
        """
        from th_pocket.models import Pocket as PocketModel

        pocket_instance = ''

        if token and 'link' in data and data['link'] is not None and len(data['link']) > 0:
            # get the pocket data of this trigger
            trigger = PocketModel.objects.get(trigger_id=trigger_id)

            pocket_instance = pocket.Pocket(
                settings.TH_POCKET['consumer_key'], token)

            title = ''
            title = (data['title'] if 'title' in data else '')
            try:
                pocket_instance.add(
                    url=data['link'], title=title, tags=(trigger.tag.lower()))

                sentence = str('pocket {} created').format(data['link'])
                logger.debug(sentence)
            except Exception as e:
                logger.critical(e)

        else:
            logger.critical("no token provided for trigger ID %s ", trigger_id)

    def auth(self, request):
        """
            let's auth the user to the Service
        """
        callbackUrl = 'http://%s%s' % (
            request.get_host(), reverse('pocket_callback'))

        request_token = Pocket.get_request_token(
            consumer_key=settings.TH_POCKET['consumer_key'],
            redirect_uri=callbackUrl)

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
            # 1) we get the previous object
            us = UserService.objects.get(
                user=request.user,
                name=ServicesActivated.objects.get(name='ServicePocket'))
            # 2) then get the token
            access_token = Pocket.get_access_token(
                consumer_key=settings.TH_POCKET['consumer_key'],
                code=request.session['request_token'])

            us.token = access_token
            # 3) and save everything
            us.save()
        except KeyError:
            return '/'

        return 'pocket/callback.html'
