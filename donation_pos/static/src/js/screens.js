odoo.define('pos_order_line.screens', function (require) {

    "use strict";
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');

    var _t = core._t;
    var round_pr = utils.round_precision;
    var leq_zero_qty = (ol) => ol.get_quantity() <= 0;

    // This configures write action for contribution line. A contribution line contains a
    // contribution percentage and a contribution product ID and it's price is calculated
    // based on the remaining order lines
    screens.PaymentScreenWidget.include({
        recompute_contribution: function () {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();

            // Check if order already has a contribution order line
            var order_has_donation = false
            if (orderlines.length == 0) { return }

            for (var i = 0, len = orderlines.length; i < len; i++) {
                var orderline = orderlines[i]

                if (orderline.get_donation() == 1) {
                    order_has_donation = true
                    orderline.set_unit_price(order.get_contribution())
                    break
                }
            }

            // Create donation-specific order line
            if (order_has_donation == false && this.pos.config.default_donation_product_id) {
                var donation_product = this.pos.config.default_donation_product_id
                var donation_product_id = this.pos.db.get_product_by_id(donation_product[0])

                order.add_product(donation_product_id)
                var contribution_orderline = order.get_last_orderline()
                contribution_orderline.set_donation(1)
                contribution_orderline.set_quantity(order.get_donation_quantity())
                contribution_orderline.set_unit_price(order.get_contribution())
            }

        },
        remove_donation_lines: function () {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            for (var i = 0, len = orderlines.length; i < len; i++) {
                var orderline = orderlines[i]
                orderline.remove_donation()
                this.trigger('change', this);
            }
        },
        // Auto set contribution line when entering to payment screen
        init: function (parent, options) {
            this._super(parent, options);
            this.recompute_contribution()
        },
        // Inherit show function to set default contribution
        show: function () {
            var order = this.pos.get_order();
            this.recompute_contribution()

            this._super()
        },
        // Inherit hide function to remove default contribution (avoiding unnecessary deatils in order window)
        hide: function () {
            var order = this.pos.get_order();

            if (order.finalized == false) {
                this.remove_donation_lines()
            }

            this._super()
        },
        // Donation add/change/remove funtionalities
        click_donation: function () {
            var self = this;
            var order = this.pos.get_order();
            var contribution = order.display_contribution();
            var mode = this.pos.config.auto_contribution_mode

            this.gui.show_popup('number', {
                'title': mode == 'fixed' ? _t('Donation Total') : _t('Donation %'),
                'value': self.format_currency_no_symbol(contribution),
                'confirm': function (value) {
                    order.set_contribution(value);
                    self.order_changes();
                    self.recompute_contribution()
                    self.render_paymentlines();
                }
            });
        },
        // Inherit render function to add donation editing tools
        renderElement: function () {
            var self = this;
            this._super();

            this.$('.js_donation').click(function () {
                self.click_donation();
            });
        }
    });

    // Inherit main order widget to add donation in subtotals
    screens.OrderWidget.include({
        update_summary: function () {
            this._super()

            var order = this.pos.get_order();
            if (!order.get_orderlines().length) {
                return;
            }

            var total = order ? order.get_total_with_tax() : 0;
            var donation_total = order ? order.get_donation_total() : 0;
            var total_with_donation = total
            
            if (this.pos.config.suggested_contribution_add_to_total) {
                // Donation also in total
                total_with_donation += donation_total
                
                // Display additional subtotal
                if (this.pos.config.display_subtotal_without_donation && this.pos.config.use_auto_contribution) {
                    var subtotal = total
                    this.el.querySelector('.summary .total .donation_subtotal .value').textContent = this.format_currency(subtotal);
                }
            }

            this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total_with_donation);
            this.el.querySelector('.summary .total .donation .value').textContent = this.format_currency(donation_total);
        },
    });
    
    // Inherit PosCategory to force searched produts to go through scale
    screens.ProductCategoriesWidget.include({
        perform_search: function(category, query, buy_result){
            var products;
            if(query){
                products = this.pos.db.search_product_in_category(category.id,query);
                if(buy_result && products.length === 1){
                        this.gui.current_screen.click_product(products[0]);
                        this.clear_search();
                }else{
                    this.product_list_widget.set_product_list(products);
                }
            }else{
                products = this.pos.db.get_product_by_category(this.category.id);
                this.product_list_widget.set_product_list(products);
            }
        },
    });
    
    });
