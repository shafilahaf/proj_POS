from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json

# Inherit pos.category
class PosProductCategories(models.Model):
    _inherit = 'pos.category'

    bc_id_guid = fields.Char(string='BC ID', help='The GUID of the product category in the Business Central system')
    need_to_be_sent = fields.Boolean(string='Need to be sent', help='Check this box if you want to send this product category to Business Central', default=True)
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def apply_to_all_products(self):
        products = self.env['product.template'].search([('pos_categ_id', '=', self.id)])
        for product in products:
            product.image_1920 = self.image_128
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def create_send_to_bc(self):
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/itemCategories'
        headers = {'Content-Type': 'application/json'}

        data = {
            "code": self.name,
            "description": "",
            "forPOS": True
        }

        try:
            # Check if the product category already exists in Business Central
            existing_categories_url = f'{url}?$filter=code eq \'{self.name}\''
            response = requests.get(existing_categories_url, headers=headers, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
            categories = response.json().get('value', [])

            if categories:
                # Product category already exists, update local fields accordingly
                self.bc_id_guid = categories[0]['Id']
                self.need_to_be_sent = False
            else:
                # Product category doesn't exist, create it
                response = requests.post(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
                response.raise_for_status()

                if response.status_code == 201:
                    self.bc_id_guid = response.json()['Id']
                    self.need_to_be_sent = False
        except requests.exceptions.RequestException as e:
            raise ValidationError(e)

        
    def write_send_to_bc(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/itemCategories(' + self.bc_id_guid + ')'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/itemCategories({self.bc_id_guid})'
        headers = {
            'If-Match': '*'
        }

        data = {
            "code": str(self.name),
            "description": "",
            "forPOS": True
        }

        try:
            response = requests.patch(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValidationError(e)
        
    @api.model
    def create(self, vals):
        record = super(PosProductCategories, self).create(vals)
        if record.need_to_be_sent and record.company.integrate_to_bc == True:
            record.create_send_to_bc()
        return record
    
    def write(self, vals):
        res = super(PosProductCategories, self).write(vals)
        if vals.get('name') and self.bc_id_guid:
            self.write_send_to_bc()
        return res