odoo.define('qr_static_pos.payment', function (require) {
    'use strict'

    const core = require('web.core')
    const rpc = require('web.rpc')
    const PaymentInterface = require('point_of_sale.PaymentInterface')
    const { Gui } = require('point_of_sale.Gui')
    
    const _t = core._t    
    const PaymentQrStaticPOS = PaymentInterface.extend({
        send_payment_request: function () {
            this._super.apply(this, arguments)
            this._reset_state()
            return this._qr_static_pos_pay()
        },
        get_selected_payment: function () {
            const paymentLine = this.pos.get_order().selected_paymentline
            if (paymentLine && paymentLine.payment_method.use_payment_terminal === 'pos_qr_static') {
              return paymentLine
            }
            return false
        },  

        send_payment_cancel: function () {
            this._super.apply(this, arguments)
            // set only if we are polling
            this.was_cancelled = !!this.polling
      
            // Cancel order on Xendit
//            const paymentLine = this.get_selected_payment()
//            return this._xendit_cancel(paymentLine)
        },

        close: function () {
            this._super.apply(this, arguments)
        },

        _reset_state: function () {
            this.was_cancelled = false
            this.last_diagnosis_service_id = false
            this.remaining_polls = 2
            clearTimeout(this.polling)
        },

        _qr_static_pos_pay: function () {
            const self = this

            const order = this.pos.get_order()
            const paymentLine = this.get_selected_payment()
            if (paymentLine && paymentLine.amount <= 0) {
                this._show_error(
                  _t('Cannot process transaction with zero or negative amount.')
                )
                return Promise.resolve()
            }
            const receipt_data = order.export_for_printing()
            receipt_data.amount = paymentLine.amount
            return this._call_qr_dynamic_pos(receipt_data).then(function (data) {
                return self._qr_static_pos_handle_response(data)
            })
        },
 
        _call_qr_dynamic_pos: function (data) {
            return rpc.query({
              model: 'pos.payment.method',
              method: 'generate_qr_dynamic',
              args: [data]
            }).catch(
                this._handle_odoo_connection_failure.bind(this)
            )
        },
        _qr_static_pos_handle_response: function (response) {
            const self = this;
            const order = this.pos.get_order();
            const paymentLine = this.get_selected_payment();
            order.setqrDynamic(response);

//            Gui.showPopup('ErrorPopup', {
//                title: 'Dynamic QRcode',
//                body: order.getqrDynamic()
//            })            
            Gui.showPopup('QRConfirmPopup', {
                title: _t('Scan to pay')
            });

            let canvasShown = false
            let countShowCanvas = 10
            const showCanvasInterval = setInterval(function () {
              canvasShown = self.convert_image_to_canvas(order.getqrDynamic())
              countShowCanvas++
              if (canvasShown || countShowCanvas >= 10) {
                clearInterval(showCanvasInterval)
              }
            }, 500)

            paymentLine.set_payment_status('waiting')
        },
        
        convert_image_to_canvas: function (image_url) {
            const canvas = document.getElementById('canvas-qrcode')
            if (canvas == null || canvas.length === 0) {
              return false
            }
       
            canvas.height = 290
            canvas.width = 290
            const ctx = canvas.getContext('2d')
      
            // create new image object to use as pattern
            const img = new Image()
            img.src = image_url
            img.onload = function () {
              const scale = Math.max(canvas.width / img.width, canvas.height / img.height)
              const x = (canvas.width / 2) - (img.width / 2) * scale
              const y = (canvas.height / 2) - (img.height / 2) * scale
              ctx.drawImage(img, x, y, img.width * scale, img.height * scale)
            }
      
            return true
        },
        _handle_odoo_connection_failure: function (data) {
            const paymentLine = this.get_selected_payment()
            if (paymentLine) {
              paymentLine.set_payment_status('retry')
            }
      
            this._show_error(_t('Could not connect to the Odoo server, please check your internet connection and try again.'))
            return Promise.reject(data) 
          }, 
          _show_error: function (title, msg) {
            if (!title) {
              title = _t('QR Error')
            }
            Gui.showPopup('ErrorPopup', {
              title,
              body: msg
            })
          },                 
                  
    })    
    return PaymentQrStaticPOS
});