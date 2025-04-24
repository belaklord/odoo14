from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from geopy import distance

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.tools.float_utils  import float_round 



class CanjeoPuntos(WebsiteSale):

    #Boton de canjear puntos#
    @http.route(['/shop/puntos'], type='http', auth="public", website=True, sitemap=False)
    def puntos(self, puntos, **post):
        redirect = post.get('r', '/shop/cart')
        order = request.website.sale_get_order()

        if puntos != '' :
            puntos_usados = int(puntos)
        usuario_pedidos = order.partner_id.name
        ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
        puntos_usuario = int(ficha_usuarios.x_puntos) #puntos totales del usuario

        if ficha_usuarios.x_puntosRestantes == 0:
            ficha_usuarios.x_puntos_usados = puntos_usados
            puntos_restantes_utilizados = ficha_usuarios.x_puntosRestantes
            aplica_punto = False

            if puntos and int(puntos) < puntos_usuario and puntos_usados % 50 == 0 and puntos_restantes_utilizados == 0 and puntos_usados >= 100:

                total_pedido = order.amount_total
                mitad_pedido = total_pedido / 2

                cambio_puntos_usados = (puntos_usados / 50)
           
            #quitar el iva de la ficha del produto descuento

                if cambio_puntos_usados < mitad_pedido:

       
                    puntos_restantes =  puntos_usuario - puntos_usados #puntos restantes del usuario tras utililzarlos.

                    for punto in order.order_line:
                        if punto.product_id.name == 'Canjeo': #sumar los puntos perdidos al eliminar el descuento.
                            punto.unlink()


                    order.write({

                    'order_line': [
                    (0,0, {
                    'order_id': order.id,
                    'product_id': 3625,
                    #'price_unit':    - cambio_puntos_usados, Descuento calculado#
                    'product_uom_qty': cambio_puntos_usados,
                    'is_reward_line': False,
                    
                    
                        })
                        ]
                        })

                    ficha_usuarios.x_puntos = ficha_usuarios.x_puntos - puntos_usados
                    ficha_usuarios.x_puntosRestantes = puntos_usados


                elif cambio_puntos_usados > mitad_pedido:

                    return request.redirect("%s?error_puntos_mayor_pedido=1" % redirect)


            elif ficha_usuarios.x_puntos < puntos_usados or puntos_usados% 100 != 0 :
           
                return request.redirect("%s?error_puntos_insuficientes=1" % redirect)


            else:
             #revisar los mensajes de error---destapan todos los formularios#
                return request.redirect("%s?error_puntos=1" % redirect)


            request.website.sale_get_order(code=puntos)
            return request.redirect(redirect)

        else:

            return request.redirect("%s?error_puntos=1" % redirect) 




    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment_puntos(self, **post):
        res = super(CanjeoPuntos, self).payment_puntos()
        #res = super().payment()
        order = request.website.sale_get_order()
        partner_id = order.partner_shipping_id
        partner_id.geo_localize()
        hairdressers = self._get_haidressers(partner_id)
        #precio_pedido = self._get_precioPedido(order)
        plazos_pago = []

        
        #fin plazos de pago dispnible


        #Canjeo puntos PVP#
        if order.website_id.name == 'Versum' :
            usuario_pedidos = order.partner_id.name
            ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
            puntos_usados_usuario = ficha_usuarios.x_puntos_usados
            cambio_puntos_usados = (puntos_usados_usuario / 50)
            aplica_punto = False


            for lineas in order.order_line:
                if lineas.product_id.name == 'Canjeo':
                    lineas.unlink()
                    aplica_punto = True


            if aplica_punto == True :
                order.write({

                            'order_line': [
                            (0,0, {
                            'order_id': order.id,
                            'product_id': 3625,
                            #'price_unit':   , #Descuento calculado#
                            'product_uom_qty': cambio_puntos_usados,
                            'is_reward_line': False,
                            
                            })
                            ]
                            })
            render_values = self._get_shop_payment_values(order, **post)
            render_values['only_services'] = order and order.only_services or False

            if render_values['errors']:
                render_values.pop('acquirers', '')
                render_values.pop('tokens', '')

            return request.render("website_sale.payment", render_values)
    


    #Controlador que se ejecuta al cambiar la cantidad de un producto en el carrito #
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)

    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        
        #Código sacado del codigo principal
        order = request.website.sale_get_order(force_create=1) #obtenemos la orden de venta actual
        descuento = False
        
        #Código sacado del codigo principal
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        #Codigo sacado del código principal
        value = order._cart_update(product_id=product_id, line_id=line_id,add_qty=add_qty,set_qty=set_qty)
        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        usuario_pedidos = order.partner_id.name
        ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
        puntos_usuario = int(ficha_usuarios.x_puntos) #puntos totales del usuario


        cambio_puntos_usados = ficha_usuarios.x_puntos_usados / 50

        for lineas in order.order_line:
            if lineas.product_id.name == 'Canjeo':
                lineas.unlink()
                descuento = True

        if descuento == True :
            order.write({

                'order_line': [
                (0,0, {
                'order_id': order.id,
                'product_id': 3625,
                #'price_unit':    , #descuento calculado#
                'product_uom_qty': cambio_puntos_usados,
                'is_reward_line': False,
                
                })
                ]
                })
        elif descuento == False :
            if ficha_usuarios.x_puntosRestantes > 0:
                ficha_usuarios.x_puntos = ficha_usuarios.x_puntos + ficha_usuarios.x_puntosRestantes
                ficha_usuarios.x_puntosRestantes = 0
            return request.redirect('/shop/cart')

         #Código sacado del codigo principal#
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
        'website_sale_order': order,
        'date': fields.Date.today(),
        'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view'].render_template("website_sale.short_cart_summary", {
        'website_sale_order': order,
        })


        return value


    @http.route(['/shop/payment/transaction/', '/shop/payment/transaction/<int:so_id>', '/shop/payment/transaction/<int:so_id>/<string:access_token>'],
                type='json', auth="public", website=True)
    
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        res = super().payment_transaction(acquirer_id, save_token, so_id, access_token, token, **kwargs)

        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)


        else:

            order = request.website.sale_get_order()

            usuario_pedidos = order.partner_id.name
            ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)]) #ficha de usuario con nombre igual al del pedido. 
            ficha_usuarios.x_puntosRestantes = 0
            total_pedido_puntos = 0

            if order.website_id.name == 'Versum':
                for lineas in order.order_line:
                    if not lineas.product_id.name == "Canjeo" and not lineas.product_id.name == "Envío":
                        total_pedido_puntos += lineas.price_total

                puntos = total_pedido_puntos * 10
                ficha_usuarios.x_puntos = ficha_usuarios.x_puntos + puntos
                ficha_usuarios.x_puntos_usados = 0
                

        return res



