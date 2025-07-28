# -*- coding: utf-8 -*-
{
    'name': "POS Product Stock Info",
    'summary': "Hide out-of-stock products and show stock on POS",
    'description': """""",
    'author': "Shahid Khan",
    'website': "https://apps.odoo.com/apps/modules/browse?search=Shahid+Khan",
    'category': 'Point of Sale',
    'version': '18.0.1.0.0',
    'depends': ["point_of_sale"],
    'data': [
        "views/res_config_setting_views.xml"
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_product_stock_info/static/src/**/*',
        ]
    },
    'demo': [],
    'license': 'LGPL-3',
}

