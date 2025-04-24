# -*- coding: utf-8 -*-

{
    'name': 'Multi-module',
    'version': '1.6',
    'summary': 'Modulo personalizado',
    'category': 'Tools',
    'depends': [
        
    ],
    'data': [
        #'data/product.xml',
        #'data/geo_localize_partner.xml',

        # backend
        'views/backend/res_config.xml',

        # frontend
        'views/frontend/assets.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
