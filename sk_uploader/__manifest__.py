# -*- coding: utf-8 -*-
{
    'name': "Uploader",
    'summary': "Dynamic Uploader",
    'description': """""",
    'author': "Shahid Khan",
    'website': "https://iamshahid.dev/",
    'category': 'Extra Tools',
    'version': '18.0.1.0.0',
    'depends': ["mail", "base"],
    'data': [
        'security/ir.model.access.csv',
        'views/uploader_template_views.xml',
        'views/uploader_uploader_views.xml',
        'views/menus.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'sk_uploader/static/src/css/uploader_styles.css',
        ],
    },
    'license': 'LGPL-3',
}
