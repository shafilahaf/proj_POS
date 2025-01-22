from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosConfigTR(models.Model):
	_inherit = 'pos.config'
	
	group_payment_id = fields.Many2one('res.groups',string='Point of Sale - Payment')
	group_change_quantity_id = fields.Many2one('res.groups',string='Point of Sale - Price')
	group_show_numpad_id = fields.Many2one("res.groups",string="Point of Sale - Show Numpad")
	group_refund_id = fields.Many2one("res.groups",string="Point of Sale - Refund")


