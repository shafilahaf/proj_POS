from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)
class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    bc_id_guid = fields.Char(string='BC ID', help='The GUID of the order in the Business Central system', readonly=True)
    need_to_be_sent = fields.Boolean(string='Need to be sent', help='Check this box if you want to send this order to Business Central', readonly=True, default=True)
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def create_send_to_bc(self):
        # url = 'http://trusta.ddns.net:21043/Kopitien/api/Trusta/pos/v1.0/companies(9abb6a44-eacb-ee11-b85c-d8bbc19ff659)/posOrders'
        url = f'{self.company.url_api}/v1.0/companies({self.company.company_bc_id.id_bc})/posOrders'
        headers = {'Content-Type': 'application/json'}

        if self.company.integrate_to_bc == False and self.company.default_customer_code == False:
            raise ValidationError('The company is not integrated to Business Central or the default customer code is not set.')
        elif self.table_id.allow_send_to_bc == False:
            return False
        elif not self.lines:
            return False
        else:

            check_url = f"{url}(orderRef='{self.name}')"
            response = requests.get(check_url, headers=headers, auth=(self.company.username_api, self.company.password_api))

            if response.status_code == 200:
                _logger.info(f"Order {self.name} already exists in Business Central. Skipping send.")
                self.need_to_be_sent = False
                return False
            elif response.status_code != 404:
                _logger.error(f"Error checking order {self.name} in BC: {response.status_code} - {response.text}")
        
        
            for line in self.lines:
                product = self.env['product.product'].search([('name', '=', line.full_product_name)], limit=1)
                if not product.discount_type and not product.bc_id_guid:
                    return False
            order_lines = []
            line_no_counter = 1
            for line in self.lines:
                combo_order_lines = []
                combo_line_no = 1
                for combo in line.combo_prod_ids:
                    combo_order_lines.append({
                        'orderRef': self.name,
                        'Document_Line_No': line_no_counter, #self.lines.ids.index(line.id) + 1,
                        'Line_No': combo_line_no,
                        'Product_No': self.env['product.product'].search([('name', '=', combo.name)], limit=1).default_code,
                        'Product_Name': combo.name,
                        'Quantity': 1,
                        'Unit_Price': self.env['product.product'].search([('name', '=', combo.name)], limit=1).list_price,
                    })
                    combo_line_no += 1
                order_lines.append({
                    'lineNo': line_no_counter,#self.lines.ids.index(line.id) + 1,
                    'orderRef': self.name,
                    'productNo': self.env['product.product'].search([('name', '=', line.full_product_name)], limit=1).default_code if self.env['product.product'].search([('name', '=', line.full_product_name)], limit=1).default_code else 'OTHER',
                    'productName': line.full_product_name,
                    'quantity': line.qty,
                    'unitPrice': line.price_unit,
                    'discountType': self.env['product.product'].search([('name', '=', line.full_product_name)], limit=1).discount_type if self.env['product.product'].search([('name', '=', line.full_product_name)], limit=1).discount_type else "",
                    'discount': line.discount,
                    'discountAmount': line.price_unit * line.qty * line.discount / 100,
                    'lineAmount': line.price_subtotal_incl,
                    'serviceCharge': True if line.tax_ids_after_fiscal_position.filtered(lambda tax: tax.name == 'Service Charge') else False,
                    'pb1': True if line.tax_ids_after_fiscal_position.filtered(lambda tax: tax.name == 'PB 1') else False, 
                    'posOrderLineDetailss': combo_order_lines,
                })
                line_no_counter += 1 + combo_line_no # Increment by number of combo lines to ensure unique Line_No

            # Get posOrderPayments
            posOrderPayments = []
            for payment in self.payment_ids:
                if not any(d['paymentMethod'] == payment.payment_method_id.name for d in posOrderPayments):
                    posOrderPayments.append({
                        'orderRef': self.name,
                        'paymentMethod': payment.payment_method_id.name,
                        'date': payment.payment_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'amount': sum(p.amount for p in self.payment_ids if p.payment_method_id.name == payment.payment_method_id.name),
                    })

            data = {
                'orderRef': self.name,
                'date': self.date_order.strftime('%Y-%m-%d'),
                'transactionDate': self.date_order.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'cashier': self.user_id.name,
                'receiptNo': self.pos_reference,
                'session': self.session_id.name,
                'tableName': self.table_id.name if self.table_id else '',
                'totalGuest': self.customer_count if self.customer_count else 0,
                'Customer': self.company_id.default_customer_code.code if self.company_id.default_customer_code else '',
                'posOrderLines': order_lines,
                'posOrderPayments': posOrderPayments,
                'roundingAmount': self.amount_paid - self.amount_total,
            }

            # raise ValidationError(json.dumps(data, indent=4))
            response = requests.post(url, headers=headers, json=data, auth=(self.company.username_api, self.company.password_api))
            if response.status_code == 201:
                self.need_to_be_sent = False
            else:
                raise ValidationError(f"Failed to send order: {response.status_code} - {response.text}")
            
            return True
        
        # Scheduler to send the orders to BC
    def scheduler_send_to_bc(self):
        pos_orders = self.env['pos.order'].search([('need_to_be_sent', '=', True), ('state', '=', 'done')])
        try:
            for pos_order in pos_orders:
                pos_order.create_send_to_bc()
            return True
        except Exception as e:
            raise ValidationError(e)
    
class PosOrderWizard(models.TransientModel):
    _name = 'pos.order.wizard'
    _description = 'Pos Order Wizard'

    start_datetime = fields.Datetime(string='Start Date', required=True)
    end_datetime = fields.Datetime(string='End Date', required=True)
    description = fields.Text(string='Description', default='This wizard will bulk insert all the POS orders to Business Central', readonly=True)

    # Bulk insert tp BC
    def bulk_insert_to_bc(self):

        pos_orders = self.env['pos.order'].search([('need_to_be_sent', '=', True), ('date_order', '>=', self.start_datetime), ('date_order', '<=', self.end_datetime), ('state', '=', 'done')]) #('need_to_be_sent', '=', True), 
        try:
            for pos_order in pos_orders:
                pos_order.create_send_to_bc()
            return True
        except Exception as e:
            raise ValidationError(e)