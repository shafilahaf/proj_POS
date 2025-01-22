# -*- coding: utf-8 -*-
# from odoo import http


# class PosTrustaTicketScreen(http.Controller):
#     @http.route('/pos_trusta_ticket_screen/pos_trusta_ticket_screen', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_trusta_ticket_screen/pos_trusta_ticket_screen/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_trusta_ticket_screen.listing', {
#             'root': '/pos_trusta_ticket_screen/pos_trusta_ticket_screen',
#             'objects': http.request.env['pos_trusta_ticket_screen.pos_trusta_ticket_screen'].search([]),
#         })

#     @http.route('/pos_trusta_ticket_screen/pos_trusta_ticket_screen/objects/<model("pos_trusta_ticket_screen.pos_trusta_ticket_screen"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_trusta_ticket_screen.object', {
#             'object': obj
#         })
