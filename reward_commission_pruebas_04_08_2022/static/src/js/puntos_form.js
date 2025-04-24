odoo.define('reward_commission.puntos_form', function(require) {
    "use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');
var VariantMixin = require('sale.VariantMixin');
var wSaleUtils = require('website_sale.utils');

var _t = core._t;


publicWidget.registry.WebsiteSale = publicWidget.Widget.extend(VariantMixin, {
selector: '.oe_website_sale',
events: _.extend({}, VariantMixin.events || {}, {
    
    'click .puntos': '_onClickShowPuntos',
    'click .show_coupon': '_onClickShowCoupon',
    'click .a-submit': '_onClickSubmit','change form .js_product:first input[name="add_qty"]': '_onChangeAddQuantity',
    'mouseup .js_publish': '_onMouseupPublish',
    'touchend .js_publish': '_onMouseupPublish',
    'click .oe_cart a.js_add_suggested_products': '_onClickSuggestedProduct',
    'click a.js_add_cart_json': '_onClickAddCartJSON',
    'change .oe_cart input.js_quantity[data-product-id]': '_onChangeCartQuantity',
    
}),



 _onClickShowCoupon: function (ev) {
        $(ev.currentTarget).hide();
        $('.coupon_form').removeClass('d-none');
    },

_onClickShowPuntos: function (ev) {
    $(ev.currentTarget).hide();
    $('.puntosForm').removeClass('d-none');
    },


_onClickSubmit: function (ev, forceSubmit) {
    if ($(ev.currentTarget).is('#add_to_cart, #products_grid .a-submit') && !forceSubmit) {
        return;
    }
    var $aSubmit = $(ev.currentTarget);
    if (!ev.isDefaultPrevented() && !$aSubmit.is(".disabled")) {
        ev.preventDefault();
        $aSubmit.closest('form').submit();
    }
    if ($aSubmit.hasClass('a-submit-disable')){
        $aSubmit.addClass("disabled");
    }
    if ($aSubmit.hasClass('a-submit-loading')){
        var loading = '<span class="fa fa-cog fa-spin"/>';
        var fa_span = $aSubmit.find('span[class*="fa"]');
        if (fa_span.length){
            fa_span.replaceWith(loading);
        } else {
            $aSubmit.append(loading);
        }
    }
},

 _onChangeAddQuantity: function (ev) {
        this.onChangeAddQuantity(ev);
    },

_onMouseupPublish: function (ev) {
        $(ev.currentTarget).parents('.thumbnail').toggleClass('disabled');
    },

_onChangeAddQuantity: function (ev) {
        this.onChangeAddQuantity(ev);
    },

 

 _onClickSuggestedProduct: function (ev) {
    $(ev.currentTarget).prev('input').val(1).trigger('change');
},

 _onClickAddCartJSON: function (ev){
        this.onClickAddCartJSON(ev);
    },

_onChangeCartQuantity: function (ev) {
    var $input = $(ev.currentTarget);
    if ($input.data('update_change')) {
        return;
    }
    var value = parseInt($input.val() || 0, 10);
    if (isNaN(value)) {
        value = 1;
    }
    var $dom = $input.closest('tr');
    // var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
    var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
    var line_id = parseInt($input.data('line-id'), 10);
    var productIDs = [parseInt($input.data('product-id'), 10)];
    this._changeCartQuantity($input, value, $dom_optional, line_id, productIDs);
},


_changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
        _.each($dom_optional, function (elem) {
            $(elem).find('.js_quantity').text(value);
            productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
        });
        $input.data('update_change', true);

        this._rpc({
            route: "/shop/cart/update_json",
            params: {
                line_id: line_id,
                product_id: parseInt($input.data('product-id'), 10),
                set_qty: value
            },
        }).then(function (data) {
            $input.data('update_change', false);
            var check_value = parseInt($input.val() || 0, 10);
            if (isNaN(check_value)) {
                check_value = 1;
            }
            if (value !== check_value) {
                $input.trigger('change');
                return;
            }
            if (!data.cart_quantity) {
                return window.location = '/shop/cart';
            }
            $input.val(data.quantity);

            wSaleUtils.updateCartNavBar(data);
            wSaleUtils.showWarning(data.warning);
        });
    },


});

});

