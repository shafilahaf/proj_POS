# -*- coding: utf-8 -*-
# from odoo import http


# class PosTrustaNumpadModification(http.Controller):
#     @http.route('/pos_trusta_numpad_modification/pos_trusta_numpad_modification', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_trusta_numpad_modification/pos_trusta_numpad_modification/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_trusta_numpad_modification.listing', {
#             'root': '/pos_trusta_numpad_modification/pos_trusta_numpad_modification',
#             'objects': http.request.env['pos_trusta_numpad_modification.pos_trusta_numpad_modification'].search([]),
#         })

#     @http.route('/pos_trusta_numpad_modification/pos_trusta_numpad_modification/objects/<model("pos_trusta_numpad_modification.pos_trusta_numpad_modification"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_trusta_numpad_modification.object', {
#             'object': obj
#         })
