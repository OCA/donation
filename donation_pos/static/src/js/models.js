odoo.define('donation_pos.models', function (require) {

    "use strict";
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var _t = core._t;

    var _super_ = models.Orderline.prototype;
    var OrderLineWithDonation = models.Orderline.extend({

        // /////////////////////////////
        // Overload Section
        // /////////////////////////////
        initialize: function (session, attributes) {
            this.donation = 0;
            return _super_.initialize.call(this, session, attributes);
        },

        init_from_JSON: function (json) {
            _super_.init_from_JSON.call(this, json);
            this.donation = json.donation || 0;
        },

        clone: function () {
            var orderline = _super_.clone.call(this);
            orderline.donation = this.donation;
            return orderline;
        },

        export_as_JSON: function () {
            var json = _super_.export_as_JSON.call(this);
            json.donation = this.get_donation();
            return json;
        },

        export_for_printing: function () {
            var result = _super_.export_for_printing.call(this);
            result.donation_quantity = this.get_donation();
            return result;
        },

        // /////////////////////////////
        // Custom Section
        // /////////////////////////////

        set_donation: function (don) {
            this.order.assert_editable();

            // Update donation value.
            this.donation = don;
            this.trigger('change', this);

        },

        reset_donation: function () {
            this.donation = 0;
        },

        get_donation: function () {
            return this.donation;
        },

        remove_donation: function () {
            if (this.donation && this.order) {
                this.order.remove_orderline(this)
            }
        },

    });


    models.Orderline = OrderLineWithDonation;


    var _super_order = models.Order.prototype;
    var OrderWithDonation = models.Order.extend({

        // /////////////////////////////
        // Overload Section
        // /////////////////////////////
        initialize: function (attributes, options) {
            var res = _super_order.initialize.call(this, attributes, options);
            this.contribution = 0

            if (this.pos.config.use_auto_contribution) {
                if (this.pos.config.auto_contribution_mode == 'fixed') {
                    this.contribution = this.pos.config.contribution_default_fixed_value
                } else {
                    this.contribution = this.pos.config.contribution_default_percentage_value
                }
            }
            this.order_has_donation = false

            return res
        },

        init_from_JSON: function (json) {
            _super_order.init_from_JSON.call(this, json);
            this.contribution = json.contribution || 0;
        },

        clone: function () {
            var orderline = _super_order.clone.call(this);
            orderline.contribution = this.contribution;
            return orderline;
        },

        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.call(this);
            json.contribution = this.get_contribution();
            return json;
        },

        export_for_printing: function () {
            var result = _super_order.export_for_printing.call(this);
            result.contribution = this.get_contribution();
            return result;
        },

        // /////////////////////////////
        // Custom Section
        // /////////////////////////////

        set_contribution: function (percentage_or_fixed_value) {
            this.assert_editable();

            // Update contribution value.
            this.contribution = percentage_or_fixed_value;
            this.set('contribution', percentage_or_fixed_value);

        },

        get_contribution: function () {
            // divide contribution by 100 if in percentage mode
            if (this.pos.config.auto_contribution_mode == 'fixed') return this.contribution
            return this.contribution / 100
        },

        display_contribution: function () {
            // used only for display
            if (this.pos.config.auto_contribution_mode == 'fixed') return this.contribution
            return this.contribution
        },

        get_non_donation_total: function () {
            var orderlines = this.get_orderlines();
            var total = 0

            for (var i = 0, len = orderlines.length; i < len; i++) {
                var orderline = orderlines[i]

                if (orderline.get_donation() != 1) {
                    total += orderline.price * orderline.quantity
                }
            }

            return total
        },

        get_donation_total: function () {
            if (this.pos.config.use_auto_contribution) {
                if (this.pos.config.auto_contribution_mode == 'percentage') {
                    return this.get_contribution() * this.get_non_donation_total();
                } else {
                    return this.contribution
                }
            }
            return 0
        },

        get_donation_quantity: function () {
            // returns 1 for fixed mode - non donation total for percentage mode
            if (this.pos.config.auto_contribution_mode == 'fixed') return 1
            return this.get_non_donation_total()
        },

    });

    models.Order = OrderWithDonation;

});
