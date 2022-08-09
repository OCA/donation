odoo.define('donation_pos.db', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields("product.product", ['donation']);
});
