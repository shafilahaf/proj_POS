odoo.define("pos_trusta_numpad_modification.NumpadWidget", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const NumpadWidget = require("point_of_sale.NumpadWidget");

    const PosNumpadWidget = (NumpadWidget) =>
        class extends NumpadWidget {

            get hasquantityControl() {
                return this.env.pos.get_cashier().hasquantityControl;
            }

            get hasShowNumpadControl() {
                return this.env.pos.get_cashier().hasGroupShowNumpad;
            }


        }; 


    Registries.Component.extend(NumpadWidget, PosNumpadWidget);

    return NumpadWidget;
});
