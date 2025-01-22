from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)
# Inherit product.template model
class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    bc_id_guid = fields.Char(string='BC ID', help='The GUID of the product in the Business Central system', readonly=True)
    need_to_be_sent = fields.Boolean(string='Need to be sent', help='Check this box if you want to send this product to Business Central', default=True, readonly=True)
    is_package = fields.Boolean(string='Is Package', help='Check this box if this product is a package', default=False)
    package_line_ids = fields.One2many('pos.product.detail.package', 'product_id', string='Package Lines', help='The package lines of the product')
    bc_bom_no = fields.Char(string='BC Recipe No', help='The BOM No of the product in the Business Central system', readonly=True)
    taxes_id = fields.Many2many('account.tax', domain=[('is_default_pos_tax', '=', True)])
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def default_get(self, fields):
        """
        This function will automatically fill the taxes_id field with the taxes that have is_default_pos_tax set to True"""
        res = super(ProductTemplateInherit, self).default_get(fields)
        res['taxes_id'] = self.env['account.tax'].search([('is_default_pos_tax', '=', True)]).ids
        # Default uom to 'PORSI'
        res['uom_id'] = self.env['uom.uom'].search([('name', '=', 'PORSI')], limit=1).id
        res['uom_po_id'] = self.env['uom.uom'].search([('name', '=', 'PORSI')], limit=1).id
        return res
    
    def create_send_to_bc_recipe(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/recipes'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/recipes'
        headers = {'Content-Type': 'application/json'}

        recipe_lines = []
        for line in self.package_line_ids:
            recipe_lines.append({
                'documentNo': str(self.default_code),
                'lineNo': line.line_no,
                'no': str(line.products.default_code),
                'quantityPer': line.qty,
            })

        data = {
            'no': str(self.default_code),
            'description': self.name,
            'unitOfMeasureCode' : self.uom_id.name,
            'recipeLines': recipe_lines,
        }

        try:
            # response = requests.post(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
            response = requests.post(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
            if response.status_code == 201:
                self.bc_bom_no = response.json()['id']
        except requests.exceptions.RequestException as e:
            raise ValidationError('Error: ' + str(e))

    def create_send_to_bc_items(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/items'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/items'
        headers = {'Content-Type': 'application/json'}

        data = {
            "number": str(self.default_code),
            "displayName": self.name if self.name else '',
            "itemCategoryCode": self.pos_categ_id.name if self.pos_categ_id else '',
            'baseUnitOfMeasure': self.uom_id.name if self.uom_id else '',
            'recipeNo': str(self.default_code) if self.is_package else '',
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
            # "itemCategoryCode": self.pos_categ_id.name if self.pos_categ_id else '',
            "itemCategoryCode" : self.pos_categ_id.parent_id.name if self.pos_categ_id.parent_id else self.pos_categ_id.name,
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
        
    def write_send_to_bc_recipe(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/recipes(' + self.bc_bom_no + ')'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/recipes({self.bc_bom_no})'
        headers = {
            'If-Match': '*'
        }
        # Lines
        recipe_lines = []
        for line in self.package_line_ids:
            recipe_lines.append({
                'documentNo': str(self.default_code),
                'lineNo': line.line_no,
                'no': str(line.products.default_code),
                'quantityPer': line.qty,
            })
        data = {
            'no': str(self.default_code),
            'description': self.name,
            'unitOfMeasureCode' : self.uom_id.name,
            'recipeLines': recipe_lines,
        }
        try:
            # response = requests.patch(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
            response = requests.patch(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValidationError(e)

    @api.model
    def create(self, vals):
        record = super(ProductTemplateInherit, self).create(vals)
        if record.need_to_be_sent:
            if record.is_package:
                record.create_send_to_bc_recipe()
            record.create_send_to_bc_items()
        return record
    

    def write(self, vals):
        res = super(ProductTemplateInherit, self).write(vals)
        if vals.get('name') or vals.get('default_code') or vals.get('pos_categ_id') or vals.get('uom_id') or vals.get('list_price') or vals.get('need_to_be_sent') or vals.get('is_package') or vals.get('package_line_ids'):
            if self.bc_id_guid:
                self.write_send_to_bc_items()
            if self.is_package and self.bc_bom_no:
                self.write_send_to_bc_recipe()
    
    # def create_production_boms_bc(self):
    #     url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/prodBoms'
    #     headers = {'Content-Type': 'application/json'}

    #     production_boms = []
    #     for line in self.package_line_ids:
    #         production_boms.append({
    #             'versionCode': '',
    #             'lineNo': line.line_no,
    #             'productionBOMNo': str(self.default_code),
    #             'type': line.type,
    #             'no': str(line.products.default_code),
    #             'quantityPer': line.qty,
    #         })

    #     data = {
    #         'no': str(self.default_code),
    #         'description': self.name,
    #         'unitOfMeasureCode' : self.uom_id.name,
    #         'prodbomLines': production_boms,
    #     }

    #     try:
    #         response = requests.post(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
    #         response.raise_for_status()
    #         if response.status_code == 201:
    #             self.bc_bom_no = response.json()['no']
    #     except requests.exceptions.RequestException as e:
    #         raise ValidationError('Error: ' + str(e))

    # def create_send_to_bc(self):
    #     url = 'http://trusta.ddns.net:21043/Kopitien/api/v2.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/items'
    #     headers = {'Content-Type': 'application/json'}

    #     data = {
    #         "number": str(self.default_code),
    #         "displayName": self.name,
    #         "itemCategoryCode": self.pos_categ_id.name if self.pos_categ_id else '',
    #         'baseUnitOfMeasureCode': self.uom_id.name,
    #     }
    #     response = requests.get(url, auth=('admin', 'P@ssw0rd.1'))
    #     response.raise_for_status()
    #     if response.status_code == 200:
    #         # Create if there's no same number
    #         if not any(d['number'] == str(self.default_code) for d in response.json()['value']):
    #             try:
    #                 response = requests.post(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
    #                 response.raise_for_status()

    #                 if response.status_code == 201:
    #                     self.bc_id_guid = response.json()['id']
    #                     self.need_to_be_sent = False
    #                     if self.is_package:
    #                         self.create_production_boms_bc()
    #             except requests.exceptions.RequestException as e:
    #                 raise ValidationError(e)
    #         else:
    #             for d in response.json()['value']:
    #                 if d['number'] == str(self.default_code):
    #                     self.bc_id_guid = d['id']
    #                     self.need_to_be_sent = False
    #                     if self.is_package:
    #                         self.create_production_boms_bc()
    #     else:
    #         raise ValidationError('Error: ' + str(response.status_code))
        
    # def write_send_to_bc(self):
    #     url = 'http://trusta.ddns.net:21043/Kopitien/api/v2.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/items(' + self.bc_id_guid + ')'
    #     headers = {
    #         'If-Match': '*'
    #     }

    #     data = {
    #         "number": str(self.default_code),
    #         "displayName": self.name if self.name else '',
    #         "itemCategoryCode": self.pos_categ_id.name if self.pos_categ_id else '',
    #         'baseUnitOfMeasureCode': self.uom_id.name,
    #     }
    #     _logger.info('See data: ' + str(data))
    #     try:
    #         response = requests.patch(url, headers=headers, json=data, auth=('admin', 'P@ssw0rd.1'))
    #         response.raise_for_status()
    #     except requests.exceptions.RequestException as e:
    #         raise ValidationError(e)
    
    # @api.model
    # def create(self, vals):
    #     record = super(ProductTemplateInherit, self).create(vals)
    #     if record.need_to_be_sent:
    #         record.create_send_to_bc()
    #     return record
    
    # def write(self, vals):
    #     res = super(ProductTemplateInherit, self).write(vals)
    #     if vals.get('name') and self.bc_id_guid:
    #         self.write_send_to_bc()
    #     return res