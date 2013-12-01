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


logger = getLogger('django_th.trigger_happy')


class ServicePocket(ServicesMgr):

    def save_data(self, access_token, title, url, trigger_id, extra=''):

        if access_token and len(url) > 0 and len(title):
            # get the pocket data of this trigger
            trigger = Pocket.objects.get(trigger_id=trigger_id)

            pocket_instance = pocket.Pocket(
                settings.TH_POCKET['consummer_key'], access_token)

            pocket_instance.add(
                url=url, title=title, tags=(trigger.tag.lower()))

            logger.debug(sentance)

        else:
            logger.critical(
                "no token provided for trigger ID %s and title %s", trigger_id, title)

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
