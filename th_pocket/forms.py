# -*- coding: utf-8 -*-

from django import forms
from th_pocket.models import Pocket


class PocketForm(forms.ModelForm):

    """
        for to handle Pocket service
    """

    class Meta:
        model = Pocket
        fields = ('tag',)


class PocketProviderForm(PocketForm):
    pass


class PocketConsummerForm(PocketForm):
    pass
