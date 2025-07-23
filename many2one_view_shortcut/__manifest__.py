# -*- coding: utf-8 -*-
{
    'name': "Many2one View Shortcut",
    'summary': "Enhanced Many2One Field",
    'description': """
    Add extra actions to Many2One fields with two useful buttons: one to open in a wizard, another to open in a new tab.
    """,
    'author': "Shahid Khan",
    'website': "https://github.com/shahid-0",
    'category': 'Customizations',
    "version": "18.0.1.0.1",
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': {
            'many2one_view_shortcut/static/src/**/*',
        }
    },
    'images': ['static/description/banner.gif'],
    'demo': [],
    'license': 'LGPL-3',
}

