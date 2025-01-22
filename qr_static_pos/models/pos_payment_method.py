# coding: utf-8
import logging
import json
import qrcode
import base64

from io import BytesIO

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method' 
    
    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('pos_qr_static', 'QR Static')]
    
    qr_static = fields.Text('QR Static')
    
    def convert_crc16(self, qris):
        crc = 0xFFFF
        for c in qris:
            crc ^= ord(c) << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
        hex_crc = crc & 0xFFFF
        hex_crc = f"{hex_crc:04X}"
        return hex_crc    
    
    @api.model
    def generate_qr_dynamic(self, data):
        method = self.env['pos.payment.method'].search([('use_payment_terminal', '=', 'pos_qr_static')], limit=1)
        data_01 = json.loads(json.dumps(data))
        qris = '%s' % method.qr_static
        qty = '%s' % data_01['amount']
        # Ensure qris has enough characters to avoid list index out of range
        if len(qris) < 4:
            raise ValueError("QRIS data is too short")
        qris = qris[:-4]
        step1 = qris.replace("010211", "010212")
        # Check if the split result has exactly two parts
        step2 = step1.split("5802ID")
        if len(step2) != 2:
            raise ValueError(f"Invalid QRIS format; '5802ID' not found or found multiple times in {step1}")
        uang = "54" + f"{len(qty):02d}" + qty + "5802ID"
        fix = step2[0].strip() + uang + step2[1].strip()
        fix += self.convert_crc16(fix)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(fix)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue()).decode('utf-8')
        return 'data:image/png;base64,{}'.format(qr_image)