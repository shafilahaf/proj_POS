# -*- coding: utf-8 -*-
{
    'name': "POS Trusta Numpad and Refund Button Modification",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'point_of_sale', 'product', 'pos_restaurant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/pos_config_view_tr.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_trusta_numpad_modification/static/src/js/**/*',
            # 'pos_trusta_numpad_modification/static/src/css/**/*',
        ],
        'web.assets_qweb': [
            'pos_trusta_numpad_modification/static/src/xml/**/*',
        ],
    },
}

