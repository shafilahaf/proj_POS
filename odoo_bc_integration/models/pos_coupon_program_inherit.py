from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class CouponProgramInherit(models.Model):
    _inherit = 'coupon.program'

    @api.model
    def create(self, vals):
        res = super(CouponProgramInherit, self).create(vals)
        if res.discount_line_product_id:
            res.discount_line_product_id.write({'discount_type': 'Promo', 'need_to_be_sent': False, 'taxes_id': False, 'pos_categ_id': self.env['pos.category'].search([('name', '=', 'MISC')], limit=1).id, 'sale_ok': True, 'uom_id': self.env['uom.uom'].search([('name', '=', 'Rp')], limit=1).id, 'uom_po_id': self.env['uom.uom'].search([('name', '=', 'Rp')], limit=1).id, 'available_in_pos': True})
        return res