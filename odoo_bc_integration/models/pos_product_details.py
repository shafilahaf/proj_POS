from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import xlrd
import base64
import requests

class PosProductDetailPackage(models.Model):
    _name = 'pos.product.detail.package'
    _description = 'POS Product Detail Package'

    line_no = fields.Integer(string='Line No', help='The line number of the package', store=True, compute='_compute_line_no') #, compute='_compute_line_no'
    product_id = fields.Many2one('product.template', string='Product', help='The product of the package', ondelete='cascade')
    type = fields.Selection([('Item', 'Item')], string='Type', help='The type of the package', default='Item')
    # products = fields.Many2one('product.template', string='Products', help='The products of the package', domain="[('is_package', '=', False)]")
    qty = fields.Float(string='Quantity', help='The quantity of the package', required=True)
    uom = fields.Many2one('uom.uom', string='UOM', help='The unit of measure of the package')
    id_bc = fields.Char(string='ID BC', help='The ID BC of the package')

    @api.constrains('qty')
    def _check_qty(self):
        """
        Check if the quantity is greater than zero"""
        for record in self:
            if record.qty <= 0:
                raise ValidationError(_('Quantity must be greater than zero!'))

    @api.depends('type')
    def _compute_line_no(self):
        line_number = 1
        if self.product_id:
            for line in self.env['pos.product.detail.package'].search([('product_id', '=', self.product_id.id)], order='line_no'):
                line.line_no = line_number
                line_number += 1
                
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom = self.product_id.uom_id.id

class PosProductDetailsWizard(models.TransientModel):
    _name = 'pos.product.details.wizard'
    _description = 'POS Product Details Wizard'

    uploadfile = fields.Binary(string='Upload File', help='The file to upload')

    def fnCreateProductandPackageDetails(self):
        if self.uploadfile:
            try:
                file = xlrd.open_workbook(file_contents=base64.b64decode(self.uploadfile))
                sheet = file.sheet_by_index(0)
                if sheet.nrows > 1:
                    # Name column 0, Default Code column 1, UoM column 2, Details(more than 1) column 3, Quantity for Details column 4
                    for row in range(1, sheet.nrows):
                        product = self.env['product.template'].search([('name', '=', sheet.cell(row, 0).value)])
                        if not product:
                            product = self.env['product.template'].create({
                                'name': sheet.cell(row, 0).value,
                                'default_code': sheet.cell(row, 1).value,
                                'uom_id': self.env['uom.uom'].search([('name', '=', sheet.cell(row, 2).value)]).id,
                                'is_package': True,
                                'available_in_pos': True,
                            })
                        for col in range(3, sheet.ncols, 2):
                            if sheet.cell(row, col).value:
                                package = self.env['pos.product.detail.package'].create({
                                    'product_id': product.id,
                                    'products': self.env['product.template'].search([('name', '=', sheet.cell(row, col).value)]).id,
                                    'qty': sheet.cell(row, col + 1).value,
                                    'uom': self.env['uom.uom'].search([('name', '=', sheet.cell(row, 2).value)]).id
                                })

                return {
                    'name': _('Products and Packages'),
                    'view_mode': 'tree,form',
                    'res_model': 'product.template',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'domain': [('is_package', '=', True)],
                }
            except:
                raise UserError(_('Invalid file format!'))




                                

                        
 
        
