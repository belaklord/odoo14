from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from geopy import distance

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.tools.float_utils  import float_round 



class Afiliado(WebsiteSale):

    @http.route(['/shop/afiliado'], type='http', auth="public", website=True, sitemap=False)
    def afiliado(self,codigo, **post):
        redirect = post.get('r', '/shop/cart')
        res = super().payment()
        order = request.website.sale_get_order()
        partner_id = order.partner_shipping_id
        partner_id.geo_localize()
        #precio_pedido = self._get_precioPedido(order)
        codigo_valido = True
        precio_orden = 0
        descuento_orden = 0

        if order.website_id.name == 'Versum':
            usuario_pedidos = order.partner_id.name
            ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])


            if codigo != '':
                #revisar la validez del código#

                ficha_influencer = request.env['res.partner'].sudo().search([])
                for lineas in ficha_influencer:
                    if lineas.x_Codigo_creador == codigo:
                        ficha_usuarios.x_Codigo_aplicado = codigo #codigo en la ficha del usuario (temporal)
                        codigo_valido = True
                        break
                    else:

                        codigo_valido = False

                if codigo_valido == False:
                    return request.redirect("%s?error_codigo=1" % redirect) #codigo de error#
                elif codigo_valido == True:
                    #calculo de descuento#

                    for orden in order.order_line:
                        if orden.price_total >0 and orden.product_id.name != 'Envío':
                            precio_orden += orden.price_total

                    descuento_orden = (precio_orden * 15) / 100



                    #eliminamos descuento si lo hay#
                    for pedido in order.order_line:
                        if pedido.product_id.name == 'Descuento Influencer':
                            pedido.unlink()


                    #añadimos el descueto con el valor calculado#
                    order.write({

                    'order_line': [
                    (0,0, {
                    'order_id': order.id,
                    'product_id': 3632,
                    'price_unit': - descuento_orden, #Descuento calculado#
                    'product_uom_qty': 1 ,
                    'is_reward_line': False,
                    
                    
                        })
                        ]

                        })
          
            elif codigo == '':
                return request.redirect("%s?error_codigo=1" % redirect) #codigo de error#
                
            render_values = self._get_shop_payment_values(order, **post)
            render_values['only_services'] = order and order.only_services or False

            if render_values['errors']:
                render_values.pop('acquirers', '')
                render_values.pop('tokens', '')

        request.website.sale_get_order(code=codigo)
        return request.redirect("%s?codigo_aplicado=1" % redirect)


    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)

    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):

         #Código sacado del codigo principal
        order = request.website.sale_get_order(force_create=1) #obtenemos la orden de venta actual
        influencer = False
        precio_orden = 0
        descuento_orden = 0
        
        #Código sacado del codigo principal
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        #Codigo sacado del código principal
        value = order._cart_update(product_id=product_id, line_id=line_id,add_qty=add_qty,set_qty=set_qty)
        if not order.cart_quantity:
            request.website.sale_reset()
            return value


        #codigo personalizado#

       
        if order.website_id.name == 'Versum':

            for lineas in order.order_line:
                if lineas.product_id.name == 'Descuento Influencer':
                    lineas.unlink()
                    break


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


    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def pago(self, **post):
        res = super().payment()
        order = request.website.sale_get_order()
        partner_id = order.partner_shipping_id
        partner_id.geo_localize()
        #precio_pedido = self._get_precioPedido(order)
        descuento_orden = 0
        precio_orden = 0


        #Calculo del precio del descuento en la ruta payment#

        if order.website_id.name == 'Versum':

            for orden in order.order_line:
                        if orden.price_total >0 and orden.product_id.name != 'Envío':
                            precio_orden += orden.price_total

            descuento_orden = (precio_orden * 15) / 100



            #eliminamos descuento si lo hay#
            for pedido in order.order_line:
                if pedido.product_id.name == 'Descuento Influencer':
                    pedido.unlink()


            #añadimos el descueto con el valor calculado#
            order.write({

            'order_line': [
            (0,0, {
            'order_id': order.id,
            'product_id': 3632,
            'price_unit': - descuento_orden, #Descuento calculado#
            'product_uom_qty': 1 ,
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


    
    @http.route(['/shop/payment/transaction/', '/shop/payment/transaction/<int:so_id>', '/shop/payment/transaction/<int:so_id>/<string:access_token>'],
                type='json', auth="public", website=True)


    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        res = super().payment_transaction(acquirer_id, save_token, so_id, access_token, token, **kwargs)

        #Si el cliente no elige ninguna opción y el sitio web es Easytech#

        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)

        else:

            order = request.website.sale_get_order()

            if order.website_id.name == 'Versum' :
                usuario_pedidos = order.partner_id.name
                #ficha usuario actual (el que realiza el pedido)#
                ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
                codigo_creador = ficha_usuarios.x_Codigo_aplicado
                #usuario con el código aplicado#
                ficha_influencer = request.env['res.partner'].sudo().search([('x_Codigo_creador', '=', codigo_creador)])

                
                suma_pedido = 0
                comision_influencer = 0

                #calculo de la suma de las lineas de pedido excluyendo el envío.
                for lineas in order.order_line:
                    if not lineas.product_id.name == "Envío":
                        suma_pedido += lineas.price_total

                #buscamos el cliente con el código influences aplicado


                #prueba 2% de comision del total del pedido hecho por otros#
                descuento = (suma_pedido * 2)/100
                comisiones = ficha_influencer.x_comisiones_inf
                ficha_influencer.x_comisiones_inf = descuento + comisiones
                ficha_usuarios.x_Codigo_aplicado = ''


        return res
    