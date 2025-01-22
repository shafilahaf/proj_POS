odoo.define('qr_static_pos.QRConfirmPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    // formerly ConfirmPopupWidget
    class QRConfirmPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }
 
        get currentOrder() {
            return this.env.pos.get_order();
        }
        confirm (event) {
            super.confirm()
            const pendingPaymentLine = this.currentOrder.paymentlines.find(
                paymentLine => paymentLine.payment_method.use_payment_terminal === 'pos_qr_static' &&
                    (!paymentLine.is_done() && paymentLine.get_payment_status() !== 'pending')
            );
            pendingPaymentLine.set_payment_status('done')
            this.currentOrder.resetQrDynamic()
        }
    }
    QRConfirmPopup.template = 'QRStaticPopup';
    QRConfirmPopup.defaultProps = {
        confirmText: _lt('Done'),
        cancelText: _lt('Cancel'),
        title: _lt('Confirm ?'),
        body: '',
    };

    Registries.Component.add(QRConfirmPopup);

    return QRConfirmPopup;
});
