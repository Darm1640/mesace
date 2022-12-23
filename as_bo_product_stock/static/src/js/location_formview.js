odoo.define('as_bo_product_stock.location_formview', function (require) {
"use strict";

    var FormView = require("web.FormView");

    FormView = FormView.include({
        _setSubViewLimit: function (attrs) {
            this._super.apply(this, arguments);
            if (attrs.widget === 'locationsHierarchyWidget') {
                attrs.limit = 10000;
            }
        },
    });

    return FormView

});
