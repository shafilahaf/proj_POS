from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json

class PosRestaurantTableInherit(models.Model):
    _inherit = 'restaurant.table'

    allow_send_to_bc = fields.Boolean(string="Allow Send to BC", default=False, help="Check to allow sending this table to Business Central. Uncheck to prevent sending.")