# -*- coding: utf-8 -*-

{
    'name': 'Programa de puntos',
    'version': '1.6',
    'summary': 'Reward to resellers and hairdressers by commisions',
    'category': 'Tools',
    'depends': [
        'website_sale',
        'survey',
        'base_geolocalize',
        
    ],
    'data': [
        'data/product.xml',
        'data/geo_localize_partner.xml',


        # frontend
        'views/frontend/assets.xml',
        'views/frontend/payment.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
