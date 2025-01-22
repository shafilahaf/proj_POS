from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)
# Inherit product.template model
class ProductTemplateInherit(models.Model):
    # _inherit = 'product.template'
    _inherit = 'product.product'

    bc_id_guid = fields.Char(string='BC ID', help='The GUID of the product in the Business Central system', readonly=True)
    need_to_be_sent = fields.Boolean(string='Need to be sent', help='Check this box if you want to send this product to Business Central', readonly=True, store=True, default=True)
    bc_bom_no = fields.Char(string='BC Recipe No', help='The BOM No of the product in the Business Central system', readonly=True)
    taxes_id = fields.Many2many('account.tax', domain=[('is_default_pos_tax', '=', True)])
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    discount_type = fields.Selection([('Discount', 'Discount'), ('Promo', 'Promo')], string='Discount Type')
    show_in_pos = fields.Boolean(string='Show in POS', default=True)

    @api.constrains('default_code', 'discount_type')
    def _check_default_code_required(self):
        for product in self:
            if not product.discount_type and not product.default_code:
                raise ValidationError("Internal Reference is required if Discount Type is not set.")

    @api.model
    def default_get(self, fields):
        """
        This function will automatically fill the taxes_id field with the taxes that have is_default_pos_tax set to True"""
        res = super(ProductTemplateInherit, self).default_get(fields)
        res['taxes_id'] = self.env['account.tax'].search([('is_default_pos_tax', '=', True)]).ids
        res['uom_id'] = self.env['uom.uom'].search([('name', '=', 'PORSI')], limit=1).id
        res['uom_po_id'] = self.env['uom.uom'].search([('name', '=', 'PORSI')], limit=1).id
        return res
    
    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        """
        This function will set the need_to_be_sent field to False if the discount_type is set to either 'discount' or 'promo' and True otherwise. This is to prevent the product from being sent to Business Central if it's a discount or a promo."""
        if self.discount_type:
            self.uom_id = self.env['res.company'].search([('id', '=', self.company.id)]).default_promo_uom.id
            self.uom_po_id = self.env['res.company'].search([('id', '=', self.company.id)]).default_promo_uom.id
            self.need_to_be_sent = False
        else:
            self.uom_po_id = self.env['uom.uom'].search([('name', '=', 'PORSI')], limit=1).id
            self.uom_id = self.env['uom.uom'].search([('name', '=', 'PORSI')], limit=1).id
            self.need_to_be_sent = True

    def create_send_to_bc_items(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/items'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/items'
        headers = {'Content-Type': 'application/json'}

        data = {
            "number": str(self.default_code),
            "displayName": self.name if self.name else '',
            "itemCategoryCode": self.pos_categ_id.parent_id.name if self.pos_categ_id.parent_id else self.pos_categ_id.name,
            'baseUnitOfMeasure': self.uom_id.name if self.uom_id else '',
            'unitPrice': self.list_price if self.list_price else 0,
        }
        response = requests.get(url, auth=(self.company.username_api, self.company.password_api))
        response.raise_for_status()
        if response.status_code == 200:
            # Create if there's no same number
            if not any(d['number'] == str(self.default_code) for d in response.json()['value']):
                try:
                    # response = requests.post(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
                    response = requests.post(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
                    response.raise_for_status()

                    if response.status_code == 201:
                        self.bc_id_guid = response.json()['id']
                        self.need_to_be_sent = False
                except requests.exceptions.RequestException as e:
                    raise ValidationError(e)
            else:
                for d in response.json()['value']:
                    if d['number'] == str(self.default_code):
                        self.bc_id_guid = d['id']
                        self.need_to_be_sent = False
        else:
            raise ValidationError('Error: ' + str(response.status_code))
        
    def write_send_to_bc_items(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/items(' + self.bc_id_guid + ')'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/items({self.bc_id_guid})'
        headers = {
            'If-Match': '*'
        }
        data = {
            "number": str(self.default_code),
            "displayName": self.name if self.name else '',
            "itemCategoryCode": self.pos_categ_id.parent_id.name if self.pos_categ_id.parent_id else self.pos_categ_id.name,
            'baseUnitOfMeasure': self.uom_id.name,
            'unitPrice': self.list_price,
        }
        _logger.info('See data: ' + str(data))
        try:
            # response = requests.patch(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
            response = requests.patch(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValidationError(e)

    @api.model
    def create(self, vals):
        record = super(ProductTemplateInherit, self).create(vals)
        if record.need_to_be_sent == True and record.discount_type not in ['Discount', 'Promo'] and record.default_code != False and record.company.integrate_to_bc == True:
            record.create_send_to_bc_items()
        else :
            record.need_to_be_sent = False
        return record
    

    def write(self, vals):
        res = super(ProductTemplateInherit, self).write(vals)
        if vals.get('name') or vals.get('default_code') or vals.get('pos_categ_id') or vals.get('uom_id') or vals.get('list_price') or vals.get('need_to_be_sent'):
            if self.bc_id_guid:
                self.write_send_to_bc_items()
            # if self.is_package and self.bc_bom_no:
            #     self.write_send_to_bc_recipe()