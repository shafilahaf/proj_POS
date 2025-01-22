# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class pos_trusta_ticket_screen(models.Model):
#     _name = 'pos_trusta_ticket_screen.pos_trusta_ticket_screen'
#     _description = 'pos_trusta_ticket_screen.pos_trusta_ticket_screen'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
