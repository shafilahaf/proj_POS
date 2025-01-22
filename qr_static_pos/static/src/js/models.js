odoo.define('qr_static_pos.models', function (require) {
    var models = require('point_of_sale.models');
    var PaymentQrStatic = require('qr_static_pos.payment');
    
    models.register_payment_method('pos_qr_static', PaymentQrStatic);

    const superOrder = models.Order.prototype;    
    models.Order = models.Order.extend({
        initialize: function(attr, options) {
            superOrder.initialize.call(this,attr,options);
            this.qrDynamic = this.qrDynamic  || null;
        },
        setqrDynamic: function(id) {
            this.qrDynamic = id;
            this.pos.send_current_order_to_customer_facing_display();
        },
       
        export_as_JSON: function(){
            const json = superOrder.export_as_JSON.call(this);
            json.qrDynamic = this.qrDynamic;
            return json;
        },      
        
        init_from_JSON: function(json){
            superOrder.init_from_JSON.apply(this,arguments);
            this.qrDynamic = json.qrDynamic;
        },    

        getqrDynamic: function() {
            return this.qrDynamic;
        },    
        resetQrDynamic: function() {
            this.qrDynamic = null;
            this.pos.send_current_order_to_customer_facing_display();
        },                    
    });
});