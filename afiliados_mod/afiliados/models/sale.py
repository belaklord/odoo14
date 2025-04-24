# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    commision = fields.Many2one('res.partner', 'Comision')
    
    #crea el movimiento de cuenta para el cliente (EN PROCESO) #
    def create_account_move_inf(self, partner_id,comission_inf):
        commission_influencer = self.env.ref('reward_commission.product_commission_product_template_inf')

        if partner_id and  commission_influencer:

            self.env['account.move'].sudo().create({
                'partner_id': partner_id.id,
                'type':'in_invoice',
                'invoice_line_ids': [
                    (0, None, {
                        'product_id': commission_influencer.id,
                        'quantity': 1,
                        # 'account_id': self.env.ref('l10n_es.1_account_common_4100'),
                        'price_unit': self.amount_untaxed * (comission_inf / 100),
                        'product_uom_id':1,
                        'tax_ids': [(6, 0, commission_influencer.supplier_taxes_id.ids)]
                        })
                ],
            })



    def _write(self, values):

        res = super(SaleOrder, self)._write(values)

        for saleorder in self:
            if saleorder.invoice_status == 'invoiced' and 'invoice_status' in values: #already sold . start to create reward_commission

                if saleorder.partner_id.partner_type != 'hairdresser' and  saleorder.partner_id.partner_type != 'distributor':
                    partnerid = saleorder.partner_id
                    comission_inf = 0
                    comission_inf = 3 
                    saleorder.create_account_move_inf(partnerid,comission_inf)
                    

        return res
