from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosConfigTR(models.Model):
	_inherit = 'pos.config'
	
	group_delete_order_id = fields.Many2one("res.groups",string="Point of Sale - Delete Order")


