from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError



class SaleOrder(models.Model):
    _inherit = 'sale.order' #heredamos del modelo que queremos utilizar

    #usamos la función de confirmación para gestionar las cantidades de las lineas
    def _action_confirm(self):
        """ Implementation of additionnal mecanism of Sales Order confirmation.
            This method should be extended when the confirmation should generated
            other documents. In this method, the SO are in 'sale' state (not yet 'done').
        """
        # create an analytic account if at least an expense product

        #gestion de lineas a cero
        linea_cero = False
        for order in self:
            for line in order.order_line:
                if line.product_uom_qty == 0:
                 linea_cero = True
                 break

        if linea_cero == True:
            raise UserError(_('Hay cantidades a cero'))
            return False
        else:

            for order in self:
                if any(expense_policy not in [False, 'no'] for expense_policy in order.order_line.mapped('product_id.expense_policy')):
                    if not order.analytic_account_id:
                        order._create_analytic_account()

            return True


    
   
#creamos copia del modelo para eliminar las lineas que estén a cero
class LineasPedido(models.Model): 
    _name = 'sale.order'
    _inherit = 'sale.order'


    def action_delete(self):
        for order in self:
            order.order_line.filtered(lambda l: not l.product_uom_qty).unlink()

