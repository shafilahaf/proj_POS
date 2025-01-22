odoo.define("pos_trusta_ticket_screen.models", function (require) {
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

            pos_cashier.hasGroupDeleteOrder =
                cashier &&
                cashier.groups_id.includes(
                    this.env.pos.config.group_delete_order_id[0]
                );
           
            return pos_cashier;
        },

      
    });
 
});
