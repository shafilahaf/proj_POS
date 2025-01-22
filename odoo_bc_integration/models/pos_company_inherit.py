from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class PosCompanyInherit(models.Model):
    _inherit = 'res.company'

    default_customer_code = fields.Many2one('pos.customers.trusta', string='Default Customer Code', help='Select the default customer code for the company')
    company_bc_id = fields.Many2one('company.bc', string='Company Business Central', help='Select the company from Business Central')
    url_api = fields.Char(string='URL API V1', help='Enter the URL API for the customer')
    url_api_v2 = fields.Char(string='URL API V2', help='Enter the URL API for the customer')
    username_api = fields.Char(string='Username API', help='Enter the username API for the customer')
    password_api = fields.Char(string='Password API', help='Enter the password API for the customer')

    integrate_to_bc = fields.Boolean(string='Integrate to Business Central', default=False)
    default_promo_uom = fields.Many2one('uom.uom', string='Default Promo UOM', help='Select the default promo UOM for the company')

class PosCustomers(models.Model):
    _name = 'pos.customers.trusta'
    _description = 'POS Customers Trusta'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, help='Enter the code for the customer', size=20)
    