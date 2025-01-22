odoo.define('pos_trusta_receipt_custom.CashMoveButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');

    class CashMoveButton extends PosComponent {
        async onClick() {
            this.showPopup('ErrorPopup', {
                title: _t('Error'),
                body: _t('You cannot use Cash In/Out in this PoS'),
            });
        }
    }
    CashMoveButton.template = 'point_of_sale.CashMoveButton';

    Registries.Component.add(CashMoveButton);

    return CashMoveButton;
});
