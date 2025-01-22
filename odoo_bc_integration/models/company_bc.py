from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import logging

_logger = logging.getLogger(__name__)
class CompanyBC(models.Model):
    _name = 'company.bc'
    _description = 'Company Business Central'
    _rec_name = 'displayName'

    id_bc = fields.Char(string='ID')
    name = fields.Char(string='Name')
    displayName = fields.Char(string='Display Name')
    

# Wizard
class CompanyBCWizard(models.TransientModel):
    _name = 'company.bc.wizard'
    _description = 'Company Business Central Wizard'

    description = fields.Char(string='Description', default='Get Company from Business Central')
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def get_company_bc(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/v2.0/companies'
        url = f'{self.company.url_api_v2}/v2.0/companies'
        headers = {'Content-Type': 'application/json'}

        response = requests.get(url, headers=headers, auth=(self.company.username_api, self.company.password_api))
        data = response.json()

        if 'value' in data:
            company_bc_obj = self.env['company.bc']
            # Cannot duplicate id_bc
            for company in data['value']:
                company_bc = company_bc_obj.search([('id_bc', '=', company['id'])])
                if not company_bc:
                    company_bc_obj.create({
                        'id_bc': company['id'],
                        'name': company['name'],
                        'displayName': company['displayName']
                    })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'company.bc',
                'view_mode': 'tree,form',
                'target': 'current',
                'context': {}
            }