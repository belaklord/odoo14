odoo.define('reward_commission.payment_form', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    //var publicWidget = require('web.public.widget');
    var qweb = core.qweb;
    var _t = core._t;

    
    var PaymentForm = require('payment.payment_form');
    PaymentForm.include({ //need to copy past all :(
        payEvent: function(ev) {
            ev.preventDefault();
            var form = this.el;
            var checked_radio = this.$('input[type="radio"]:checked');
            var self = this;
            if (ev.type === 'submit') {
                var button = $(ev.target).find('*[type="submit"]')[0]
            } else {
                var button = ev.target;
            }

            // first we check that the user has selected a payment method
            if (checked_radio.length === 1) {
                checked_radio = checked_radio[0];

                // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
                var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
                var acquirer_form = false;
                if (this.isNewPaymentRadio(checked_radio)) {
                    acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
                } else {
                    acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
                }
                var inputs_form = $('input', acquirer_form);
                var ds = $('input[name="data_set"]', acquirer_form)[0];

                // if the user is adding a new payment
                if (this.isNewPaymentRadio(checked_radio)) {
                    if (this.options.partnerId === undefined) {
                        console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
                    }
                    var form_data = this.getFormData(inputs_form);
                    var wrong_input = false;

                    inputs_form.toArray().forEach(function(element) {
                        //skip the check of non visible inputs
                        if ($(element).attr('type') == 'hidden') {
                            return true;
                        }
                        $(element).closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
                        $(element).siblings(".o_invalid_field").remove();
                        //force check of forms validity (useful for Firefox that refill forms automatically on f5)
                        $(element).trigger("focusout");
                        if (element.dataset.isRequired && element.value.length === 0) {
                            $(element).closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                            $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                            wrong_input = true;
                        } else if ($(element).closest('div.form-group').hasClass('o_has_error')) {
                            wrong_input = true;
                            $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                        }
                    });

                    if (wrong_input) {
                        return;
                    }

                    this.disableButton(button);
                    // do the call to the route stored in the 'data_set' input of the acquirer form, the data must be called 'create-route'
                    return this._rpc({
                        route: ds.dataset.createRoute,
                        params: form_data,
                    }).then(function(data) {
                        // if the server has returned true
                        if (data.result) {
                            // and it need a 3DS authentication
                            if (data['3d_secure'] !== false) {
                                // then we display the 3DS page to the user
                                $("body").html(data['3d_secure']);
                            } else {
                                checked_radio.value = data.id; // set the radio value to the new card id
                                form.submit();
                                return new Promise(function() {});
                            }
                        }
                        // if the server has returned false, we display an error
                        else {
                            if (data.error) {
                                self.displayError(
                                    '',
                                    data.error);
                            } else { // if the server doesn't provide an error message
                                self.displayError(
                                    _t('Server Error'),
                                    _t('e.g. Your credit card details are wrong. Please verify.'));
                            }
                        }
                        // here we remove the 'processing' icon from the 'add a new payment' button
                        self.enableButton(button);
                    }).guardedCatch(function(error) {
                        error.event.preventDefault();
                        // if the rpc fails, pretty obvious
                        self.enableButton(button);

                        self.displayError(
                            _t('Server Error'),
                            _t("We are not able to add your payment method at the moment.") +
                            self._parseError(error)
                        );
                    });
                }
                // if the user is going to pay with a form payment, then
                else if (this.isFormPaymentRadio(checked_radio)) {
                    this.disableButton(button);
                    var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
                    // if there's a prepare tx url set

                
                    if ($tx_url.length === 1) {
                        // if the user wants to save his credit card info
                        var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                        var form_haidresser_id = self.$el.find('select[name="hairdresser"]').val();
                        var form_plazos_pago = self.$el.find('select[name="plazos"]').val();
                        //var pronto_pago = self.$el.find('input[name="pronto_pago"]').prop('checked');
                        var texto_merchan = self.$el.find('textarea[name="texto-merchan"]').val();
                        

                        // then we call the route to prepare the transaction
                        return this._rpc({
                            route: $tx_url[0].value,
                            params: {
                                'acquirer_id': parseInt(acquirer_id),
                                'save_token': form_save_token,
                                'access_token': self.options.accessToken,
                                'success_url': self.options.successUrl,
                                'error_url': self.options.errorUrl,
                                'callback_method': self.options.callbackMethod,
                                'order_id': self.options.orderId,
                                'hairdresser_id' : form_haidresser_id,
                                'plazo_pago' : form_plazos_pago,
                                //'pronto_pago' : pronto_pago,
                                'merchan' : texto_merchan,
                                
                            },
                        }).then(function(result) {
                            if (result) {
                                // if the server sent us the html form, we create a form element
                                var newForm = document.createElement('form');
                                newForm.setAttribute("method", "post"); // set it to post
                                newForm.setAttribute("provider", checked_radio.dataset.provider);
                                newForm.hidden = true; // hide it
                                newForm.innerHTML = result; // put the html sent by the server inside the form
                                var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                                newForm.setAttribute("action", action_url); // set the action url
                                $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                                $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                                if (action_url) {
                                    newForm.submit(); // and finally submit the form
                                    return new Promise(function() {});
                                }
                            } else {
                                self.displayError(
                                    _t('Server Error'),
                                    _t("We are not able to redirect you to the payment form.")
                                );
                                self.enableButton(button);
                            }
                        }).guardedCatch(function(error) {
                            error.event.preventDefault();
                            self.displayError(
                                _t('Server Error'),
                                _t("We are not able to redirect you to the payment form.") + " " +
                                self._parseError(error)
                            );
                        });
                    } else {
                        // we append the form to the body and send it.
                        this.displayError(
                            _t("Cannot setup the payment"),
                            _t("We're unable to process your payment.")
                        );
                        self.enableButton(button);
                    }
                } else { // if the user is using an old payment then we just submit the form
                    this.disableButton(button);
                    form.submit();
                    return new Promise(function() {});
                }
            } else {
                this.displayError(
                    _t('No payment method selected'),
                    _t('Please select a payment method.')
                );
                this.enableButton(button);
            }
        }
    });


});
