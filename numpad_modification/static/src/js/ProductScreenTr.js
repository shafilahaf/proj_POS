odoo.define('pos_trusta_numpad_modification.ProductScreen', function(require){
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    
    const ProductScreenTr = (ProductScreen) =>
    class extends ProductScreen {
      
        get isVoidTable() {
            // Selected Table 
            const order = this.env.pos.get_order();
            const currentTable = order.table;
            return ( currentTable.id == this.env.pos.config.restaurant_table_id[0])
        }

        get hasPaymentControlRights() {
               
            return this.env.pos.get_cashier().hasGroupPayment;
        }

        get hasShowNumpadControl() {
            return this.env.pos.get_cashier().hasGroupShowNumpad;
        }

        async _onClickPay() {
            if (this.env.pos.get_order().orderlines.any(line => line.get_product().tracking !== 'none' && !line.has_valid_product_lot() && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots))) {
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Some Serial/Lot Numbers are missing'),
                    body: this.env._t('You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?'),
                    confirmText: this.env._t('Yes'),
                    cancelText: this.env._t('No')
                });
                if (confirmed) {
                    this.showScreen('PaymentScreen');
                }
            } else {
                this.showScreen('PaymentScreen');
            }

            // //TR001
            this.local = this.env.pos.config.iface_customer_facing_display_local && !this.env.pos.config.iface_customer_facing_display_proxy;
            if (this.local) {
                return this.onClickLocaltr();
            } else {
                return this.onClickProxytr();
            }

        }

         //TR
         async onClickLocaltr() {
            this.env.pos.customer_display = window.open('', 'Customer Display', 'height=600,width=900');
            const renderedHtml = await this.env.pos.render_html_for_customer_facing_display();
            var $renderedHtml = $('<div>').html(renderedHtml);
            $(this.env.pos.customer_display.document.body).html($renderedHtml.find('.pos-customer_facing_display'));
            $(this.env.pos.customer_display.document.head).html($renderedHtml.find('.resources').html());
        }
        async onClickProxytr() {
            try {
                const renderedHtml = await this.env.pos.render_html_for_customer_facing_display();
                let ownership = await this.env.pos.proxy.take_ownership_over_client_screen(
                    renderedHtml
                );
                if (typeof ownership === 'string') {
                    ownership = JSON.parse(ownership);
                }
                if (ownership.status === 'success') {
                    this.state.status = 'success';
                } else {
                    this.state.status = 'warning';
                }
                if (!this.env.pos.proxy.posbox_supports_display) {
                    this.env.pos.proxy.posbox_supports_display = true;
                    this._start();
                }
            } catch (error) {
                if (typeof error == 'undefined') {
                    this.state.status = 'failure';
                } else {
                    this.state.status = 'not_found';
                }
            }
        }
        //TR
        
    };

    Registries.Component.extend(ProductScreen, ProductScreenTr);

    return ProductScreen;
 });