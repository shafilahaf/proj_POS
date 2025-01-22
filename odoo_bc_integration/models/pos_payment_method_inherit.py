from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)
# Inherit pos.payment.method model
class PosPaymentMethodInherit(models.Model):
    _inherit = 'pos.payment.method'

    bc_id_guid = fields.Char(string='BC ID', help='The GUID of the payment method in the Business Central system')
    need_to_be_sent = fields.Boolean(string='Need to be sent', help='Check this box if you want to send this payment method to Business Central',default=True)
    name = fields.Char(size=10, required=True)
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def create_send_to_bc(self):
        url = f'{self.company.url_api_v2}/v2.0/companies({self.company.company_bc_id.id_bc})/paymentMethods'
        headers = {'Content-Type': 'application/json'}

        data = {
            "code": self.name,
            "displayName": self.name,
        }

        try:
            # Check if the payment method already exists in Business Central
            existing_payment_methods_url = f'{url}?$filter=code eq \'{self.name}\''
            response = requests.get(existing_payment_methods_url, headers=headers, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
            payment_methods = response.json().get('value', [])

            if payment_methods:
                # Payment method already exists, update local fields accordingly
                self.bc_id_guid = payment_methods[0]['id']
                self.need_to_be_sent = False
            else:
                # Payment method doesn't exist, create it
                response = requests.post(url, headers=headers, data=json.dumps(data), auth=(self.company.username_api, self.company.password_api))
                response.raise_for_status()

                if response.status_code == 201:
                    self.bc_id_guid = response.json()['id']
                    self.need_to_be_sent = False
        except requests.exceptions.RequestException as e:
            raise ValidationError(e)
        
    def write_send_to_bc(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/v2.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/paymentMethods(' + self.bc_id_guid + ')'
        url = f'{self.company.url_api_v2}/v2.0/companies({self.company.company_bc_id.id_bc})/paymentMethods({self.bc_id_guid})'
        headers = {
            'If-Match': '*'
        }

        data = {
            "code": self.name,
            "displayName": self.name
        }

        try:
            response = requests.patch(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValidationError(e)
        
        
    @api.model
    def create(self, vals):
        res = super(PosPaymentMethodInherit, self).create(vals)
        if res.need_to_be_sent and res.company.integrate_to_bc == True:
            res.create_send_to_bc()
        return res
    
    def write(self, vals):
        res = super(PosPaymentMethodInherit, self).write(vals)        
        if vals.get('name') and not self.need_to_be_sent:
            self.write_send_to_bc()
        return res