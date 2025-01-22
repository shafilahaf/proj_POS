from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    account_fiscal_country_id = fields.Char(string='Account Fiscal Country ID', help='Enter the Account Fiscal Country ID')