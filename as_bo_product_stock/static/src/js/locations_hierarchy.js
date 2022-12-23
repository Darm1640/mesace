odoo.define('as_bo_product_stock.locations_hierarchy', function (require) {
"use strict";

    var session = require('web.session');
    var registry = require('web.field_registry');
    var rpc = require("web.rpc");
    var core = require('web.core');
    var relationalFields = require('web.relational_fields');
    var qweb = core.qweb;
    var ajax = require('web.ajax');
    var dialogs = require('web.view_dialogs');
    var _t = core._t;

    ajax.loadXML('/as_bo_product_stock/static/src/xml/locations_hierarchy.xml', qweb);

    var locationsHierarchyWidget = relationalFields.FieldMany2ManyTags.extend({
        tag_template: "locationsHierarchyWidget",
        className: "o_field_many2manytags",
        fieldsToFetch: {
            name: {type: 'char'},
            qty_available: {type: 'float'},
            virtual_available: {type: 'float'},
            incoming_qty: {type: 'float'},
            outgoing_qty: {type: 'float'},
            price_unit: {type: 'float'},
        },
        events: _.extend({}, relationalFields.FieldMany2ManyTags.prototype.events, {
            'click .o_hide': '_onclickHide',
            'click .o_expand_all': '_onclickExpandAll',
        }),

        init: function () {
            // To remove input tag from the field class
            this._super.apply(this, arguments);
            if (this.mode === 'edit') {
                this.className -= ' o_input';
            };
            this.maxLevel = 2; // What is the last level to show (starts from 0)
        },

        _getRenderTagsContext: function () {
            // To retrieve hierarchy and filter zero qty
            var self = this;
            var resElements = this._super.apply(this, arguments);
            var def = $.Deferred();
            rpc.query({
                model: 'stock.location',
                method: 'prepare_elements_for_hierarchy',
                args: [{
                    "elements": resElements.elements,
                }],
            }).then(function(finalElements) {
                def.resolve({
                    elements: finalElements,
                    readonly: self.mode === "readonly"
                });
            });
            return def
        },

        _renderTags: function () {
            // To add promise
            var self = this;
            var tagIds = this._getRenderTagsContext().then(function (tagIds) {
                self.$el.html(qweb.render(self.tag_template, tagIds));
                self._hideToManyLevels();
            });
        },

        _renderEdit: function () {
            // Re-write, since we do not need M2o features here
            this._renderTags();
        },

        _onclickHide: function(event) {
            // Dummy method to catch user click of expanding / hiding
            this._onExpandHide(event)
        },

        _onExpandHide: function(event) {
            // Method to show / hide elements when there are too many of those
            var currentLocationID = $(event.target).parent().parent().data('id');
            if ($(event.target).hasClass("fa-chevron-up")) {
                // 0. In case we hide, we should hide also ALL children
                this._hideRecursive(currentLocationID);
            }
            else {
                // 1. In case we expand we should expand ONLY THE FIRST level
                $(event.target).removeClass("fa-chevron-down").addClass("fa-chevron-up");
                this._expandFirstLevel(currentLocationID);
            };
        },

        _hideRecursive: function(currentLocationID) {
            // To hide elements recursively
            var tableRes =  this.$el;
            var allRows = tableRes.find(".tr_location_class[location='" + currentLocationID.toString() + "']");

             // 0. Mark the original level as hidden
            var currentIcon = tableRes.find(".fa-chevron-up#" + currentLocationID.toString());
            currentIcon.removeClass("fa-chevron-up").addClass("fa-chevron-down");

             // 1. Hide this level
            allRows.addClass("psb_hidden");

             // 2. Change to-expand type of all children if they were previously expanded
            var iconRows = tableRes.find(".fa-chevron-up.o_hide[location='" + currentLocationID.toString() + "']");
            iconRows.removeClass("fa-chevron-up").addClass("fa-chevron-down");

             // 3.Go to the next levels recursively
            var iterator = 0;
            while (iterator != allRows.length) {
                this._hideRecursive(allRows[iterator].getAttribute("data-id"));
                iterator ++;
            }
        },

        _expandFirstLevel: function(currentLocationID) {
            // To hide elements recursively
            var tableRes =  this.$el;

             // 0. Mark the original level as expanded
            var currentIcon = tableRes.find(".fa-chevron-down#" + currentLocationID.toString());
            currentIcon.removeClass("fa-chevron-down").addClass("fa-chevron-up");

             // 1. Show this level
            var allRows = tableRes.find(".tr_location_class[location='" + currentLocationID.toString() + "']");
            allRows.removeClass("psb_hidden");
        },

        _hideToManyLevels: function() {
            // The method to hide levels through the initial rendering based on max level
            var tableRes =  this.$el;
            var allRows = tableRes.find(".tr_location_class[level='" + this.maxLevel.toString() + "']");
            var iterator = 0;
            while (iterator != allRows.length) {
                this._hideRecursive(allRows[iterator].getAttribute("data-id"));
                iterator ++;
            }
        },

        _onclickExpandAll: function(event) {
            // The method to show all levels
            var tableRes =  this.$el;
            var allRows = tableRes.find(".tr_location_class");
            var iterator = 0;
            while (iterator != allRows.length) {
                this._expandFirstLevel(allRows[iterator].getAttribute("data-id"));
                iterator ++;
            }
        }
    });

    registry.add('locationsHierarchyWidget', locationsHierarchyWidget);

});
