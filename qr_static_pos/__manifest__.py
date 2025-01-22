# -*- coding: utf-8 -*-
{
    'name': "QR Static to Dynamic POS",

    'summary': """""",

    'description': """
    """,

    'author': "Boyke Budi Pratama",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'views/pos_payment_method_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'qr_static_pos/static/src/js/qr_static_pos.js',
            'qr_static_pos/static/src/js/models.js',
            'qr_static_pos/static/src/js/qr_static_popup.js'            
        ],
        # qweb For Odoo 15.0
        'web.assets_qweb': [
            'qr_static_pos/static/src/xml/qr_static_pos_popup.xml',
            'qr_static_pos/static/src/xml/CustomerFacingDisplayOrder.xml',            
        ],
    }    
}
