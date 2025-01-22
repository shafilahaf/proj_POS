odoo.define("pos_trusta_numpad_modification.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var posmodel_super = models.PosModel.prototype;

    var exports = {};

    models.PosModel = models.PosModel.extend({
        get_cashier: function () {
            const pos_cashier = posmodel_super.get_cashier.apply(this);
            const cashier = this.env.pos.users.find(
                (user) => user.id === pos_cashier.user_id[0]
            );

            pos_cashier.hasGroupPayment = cashier && cashier.groups_id.includes(this.env.pos.config.group_payment_id[0]);
            //  // console.log(this.env.pos.config.group_change_quantity_id[0]);
            pos_cashier.hasquantityControl =
                cashier &&
                cashier.groups_id.includes(
                    this.env.pos.config.group_change_quantity_id[0]
                );

            pos_cashier.hasGroupShowNumpad =
                cashier &&
                cashier.groups_id.includes(
                    this.env.pos.config.group_show_numpad_id[0]
                );

            pos_cashier.hasGroupShowRefund =
                cashier &&
                cashier.groups_id.includes(
                    this.env.pos.config.group_refund_id[0]
                );
           
            return pos_cashier;
        },

      
    });
 
});
