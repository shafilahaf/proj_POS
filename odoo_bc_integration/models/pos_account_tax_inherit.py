from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class PosAccountTaxInherit(models.Model):
    _inherit = 'account.tax'

    is_default_pos_tax = fields.Boolean(string='Default POS Customer Tax', default=False, help='Check this box if you want to use this tax as the default tax for POS customers')