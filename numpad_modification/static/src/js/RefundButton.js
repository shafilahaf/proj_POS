odoo.define("pos_trusta_numpad_modification.RefundButton", function (require) {

    'use strict';
    const Registries = require("point_of_sale.Registries");
    const RefundButton = require("point_of_sale.RefundButton");

    const PosRefundButton = (RefundButton) =>
        class extends RefundButton {

            get hasRefundControlRights() {
               
                return this.env.pos.get_cashier().hasGroupShowRefund;
            }

        };

    Registries.Component.extend(RefundButton, PosRefundButton);

    return RefundButton;

});