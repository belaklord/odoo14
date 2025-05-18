# -*- coding: utf-8 -*-

{
    'name': 'Multi-module',
    'version': '1.6',
    'summary': 'Modulo personalizado',
    'category': 'Tools',
    'depends': [
        'crm',
        'sale',
        'website_blog',
    ],
    'data': [
        

        # backend
        'views/backend/crm.xml',
        'views/backend/botonSaleOrder.xml',
        'views/backend/blog.xml',


        # frontend
        'views/frontend/assets.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
