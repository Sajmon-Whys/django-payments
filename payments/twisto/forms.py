from __future__ import unicode_literals
from django import forms

from .. import FraudStatus, PaymentStatus
from ..forms import PaymentForm as BasePaymentForm




class PaymentForm(BasePaymentForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        widget = forms.widgets.HiddenInput()
        hidden_inputs = kwargs['hidden_inputs']
        for key, val in hidden_inputs.items():
            self.fields[key] = forms.CharField(widget=widget, initial=val)


class TwistoForm(PaymentForm):
    def __init__(self, payment, provider, **kwargs):
        super(TwistoForm, self).__init__(**kwargs)
        self.provider = provider
        self.payment = payment

    @property
    class Media:
        js = {
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            'js/payments/twisto_config.js',
            'js/payments/twisto.js'
        }

    RESPONSE_CHOICES = (
        ('3ds-disabled', '3DS disabled'),
        ('3ds-redirect', '3DS redirect'),
        ('failure', 'Gateway connection error'),
        ('payment-error', 'Gateway returned unsupported response')
    )
    status = forms.ChoiceField(choices=PaymentStatus.CHOICES)
    fraud_status = forms.ChoiceField(choices=FraudStatus.CHOICES)
    gateway_response = forms.ChoiceField(choices=RESPONSE_CHOICES)
    verification_result = forms.ChoiceField(choices=PaymentStatus.CHOICES,
                                            required=False)

    def clean(self):
        cleaned_data = super(TwistoForm, self).clean()
        gateway_response = cleaned_data.get('gateway_response')
        verification_result = cleaned_data.get('verification_result')
        if gateway_response == '3ds-redirect' and not verification_result:
            raise forms.ValidationError(
                'When 3DS is enabled you must set post validation status')
        return cleaned_data