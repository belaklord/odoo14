
from odoo import api, fields, models, tools

#Creación del campo select para el formulario del CRM
class Lead(models.Model):
     _inherit = 'crm.lead'

     fuente = fields.Selection([
          ('terceros', 'Terceros'),
          ('redes', 'Redes Sociales'),
          ('internet', 'Budsqueda en internet')], string='Fuente',)




