from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class TimeIntervals(models.Model):
    _name = 'pos.time.intervals'
    _description = 'Time Intervals'

    name = fields.Char(string='Name', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    