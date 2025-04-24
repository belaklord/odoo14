
from odoo import api, fields, models, tools


 class Lead(models.Model):
      _inherit = 'crm.lead'

      x_facturation = fields.Boolean("x_facturation", default=False)




