{
    'name': 'Model ERD Diagram',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'View ERD Diagram for any model using GoJS',
    'website': 'https://iamshahid.dev/',
    'description': """
        This module allows users to visualize the Entity Relationship Diagram (ERD) 
        of a specific model directly from the ir.model form view.
        It uses GoJS library for rendering the diagrams.
    """,
    'author': 'Shahid Khan',
    'depends': ['base', 'web'],
    'data': [
        'views/erd_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    'assets': {
        'web.assets_backend': [
            'sk_models_erd/static/lib/gojs/go.js',
            'sk_models_erd/static/src/css/erd.css',
            'sk_models_erd/static/src/xml/erd_templates.xml',
            'sk_models_erd/static/src/js/erd_client_action.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
