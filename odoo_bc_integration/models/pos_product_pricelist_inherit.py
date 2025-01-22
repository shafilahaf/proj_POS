from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import xlrd
import base64

class PosProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def fnOpenWizard(self):
        return {
            'name': _('Import Line Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.product.pricelist.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_pricelist_id': self.id},
        }

class PosProductPricelistWizard(models.TransientModel):
    _name = 'pos.product.pricelist.wizard'
    _description = 'POS Product Pricelist Wizard'

    uploadfile = fields.Binary(string='Upload Excel File')
    product_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', help='The pricelist of the product', ondelete='cascade', readonly=True)

    def fnImportProductPricelistLine(self):
        try:
            book =  xlrd.open_workbook(file_contents=base64.decodestring(self.uploadfile))
        except xlrd.biffh.XLRDError:
            raise UserError(_('The file is not an Excel file!'))
        
        for sheet in book.sheets():
            if sheet.name == 'Sheet1':
                for row in range(sheet.nrows):
                    try:
                        if row >= 1:
                            row_values = sheet.row_values(row)
                            vals = self.fnCreateBonusLineRec(row_values)

                            self.env['product.pricelist.item'].create({
                                'pricelist_id': self.product_pricelist_id.id,
                                'product_tmpl_id': vals['product_tmpl_id'],
                                'min_quantity': vals['min_quantity'],
                                'fixed_price': vals['fixed_price'],
                            })
                    except Exception as e:
                        raise UserError(_('Error in row %s: %s' % (row, e)))
    
    def fnCreateBonusLineRec(self, record):
        product = str(record[0])
        product_id = self.env['product.template'].search([('name', '=', product)], limit=1)
        line_ids = {
            'product_tmpl_id': product_id.id,
            'min_quantity': record[1],
            'fixed_price': record[2],
        }

        return line_ids