# -*- coding: utf-8 -*-
{
    'name': "Sticky Notes",
    'summary': "Quick Note-Taking from Systray",
    'description': """
        This module adds a convenient Sticky Notes feature accessible directly from the Odoo systray. 
        Users can quickly jot down notes or view existing ones without leaving their current screen. 
        It enhances productivity by allowing easy creation and management of personal or work-related notes 
        through two simple options in the systray dropdown: 'Add Note' and 'View Notes'.
    """,
    'author': "Shahid Khan",
    'website': "https://iamshahid.dev/",
    'category': 'Extra Tools',
    'version': '18.0.2.0.1',
    'depends': [],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sticky_note_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sk_sticky_notes/static/src/components/sticky_note.js',
            'sk_sticky_notes/static/src/components/sticky_note.xml',
        ]
    },
    'demo': [],
}