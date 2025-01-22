{
    'name': 'Trusta POS Modification',
    'version': '1.0',
    'description': 'This module is for POS modification for Trusta Technologies',
    'author': 'Trusta Technologies',
    'license': 'LGPL-3',
    'category': 'Services/TrustaPos',
    'depends': [
        'base', 'mail', 'point_of_sale', 'product', 'pos_restaurant'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method_inherit.xml',
        'views/product_product_inherit.xml',
        'views/pos_order_inherit.xml',
        'views/pos_product_categories_inherit.xml',
        'views/pos_product_pricelist.xml',
        'views/product_pricelist_wizard.xml',
        'views/pos_account_tax_inherit.xml',
        'views/pos_company_inherit.xml',
        'views/pos_package_details_import.xml',
        'views/company_bc_wizard.xml',
        'views/company_bc.xml',
        'views/pos_order_bulk_wizard.xml',
        'views/pos_time_intervals.xml',
        'views/pos_restaurant_table.xml'
    ],
    'installable': True,
    'application': True,
}