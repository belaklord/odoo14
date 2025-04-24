# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.http import request
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    #campo comision influencer#
    #comision_infliuencer = fields.Float(compute='_comision_influencer', string="Com. Influencer")


     #calculo de comision como en _compute_total_certification#
    def _comision_influencer(self):
        commission_product_inf = self.env.ref('reward_commission.product_commission_product_template_inf')
        account_moves_ids = self.env['account.move'].search([('partner_id', '=', self.id), ('type', 'not in', ('out_invoice', 'out_refund', 'out_receipt')), ('invoice_payment_state', '!=', 'paid')])
        total_calc = 0
        for account_move in account_moves_ids:
            for invoices_line_id in account_move.invoice_line_ids:
                if invoices_line_id.product_id == commission_product_inf:
                    total_calc = total_calc + invoices_line_id.price_total

        #self.comision_infliuencer = total_calc