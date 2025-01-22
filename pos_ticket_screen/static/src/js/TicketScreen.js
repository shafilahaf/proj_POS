odoo.define("pos_trusta_ticket_screen.TicketScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const TicketScreen = require("point_of_sale.TicketScreen");
    const { posbus } = require('point_of_sale.utils');

    const PosTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
            // constructor() {
            //     super(...arguments);

            //     useListener('delete-order', this._onDeleteOrder2);
            // }
            // async deleteOrder(order) {
            //     if (this.env.pos.get_cashier().hasGroupDeleteOrder) {
            //         return super._onDeleteOrder(order);
            //     }
            //     return false;
            // }

            async _onDeleteOrder({ detail: order }) {
                const screen = order.get_screen_data();
                if (this.env.pos.get_cashier().hasGroupDeleteOrder) {
                    if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Existing orderlines'),
                            body: _.str.sprintf(
                            this.env._t('%s has a total amount of %s, are you sure you want to delete this order ?'),
                            order.name, this.getTotal(order)
                            ),
                        });
                        if (!confirmed) return;
                    }
                    if (order && (await this._onBeforeDeleteOrder(order))) {
                        order.destroy({ reason: 'abandon' });
                        posbus.trigger('order-deleted');
                    }
                }
            }

            getTableName(order) {
                return order.table.name;
            }

            
        };

    TicketScreen.template = 'TicketScreenTr';
    TicketScreen.defaultProps = {
    destinationOrder: null,
    // When passed as true, it will use the saved _state.ui as default
    // value when this component is reinstantiated.
    // After setting the default value, the _state.ui will be overridden
    // by the passed props.ui if there is any.
    reuseSavedUIState: false,
    ui: {},
    };

    Registries.Component.extend(TicketScreen, PosTicketScreen);

    return TicketScreen;
});
