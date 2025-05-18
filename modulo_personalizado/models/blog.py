
from datetime import datetime
import random

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


#nuevo campo compañía para el modelo
class Blog(models.Model):
    _inherit = 'blog.blog'
   
    companyia = fields.Many2one('res.company', string='Compania')

#copia modelo blog y añadimos los campos requeridos
class Blog(models.Model):
    _name = 'blog.post'
    _inherit = 'blog.post'

    companyia_blog = fields.Many2one(related='blog_id.companyia', string='Compania')
    usuario_blog = fields.Char(related='blog_id.create_uid.company_name', string='usuario')
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company)


    
    



