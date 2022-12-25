odoo.define("sh_cart_ajax.website_sale", function (require) {
    "use strict";

    var sAnimations = require("website.content.snippets.animation");
    var wSaleUtils = require("website_sale.utils");

    sAnimations.registry.WebsiteSale.include({
        read_events: {
            "click .sh_add_cart, .sh_add_cart_dyn": "_onClickAddDirectCart",
        },

        /**
         * @private
         * @param {MouseEvent} ev
         */

        _onClickAddDirectCart: function (ev) {
            this._addNewProducts($(ev.currentTarget));
        },

        /**
         * @private
         */

        _addNewProducts: function ($el) {
            var self = this;
            var productID = $el.data("product-product-id");
            if ($el.hasClass("sh_add_cart_dyn")) {
                productID = $el.parent().find(".product_id").val();
                if (!productID) {
                    // case List View Variants
                    productID = $el.parent().find("input:checked").first().val();
                }
                productID = parseInt(productID, 10);
            }

            var $form = $el.closest("form");
            var $quantity_available = parseFloat($form.find("#product_available").val());
            var templateId = $form.find(".product_template_id").val();
            // when adding from /shop instead of the product page, need another selector
            if (!templateId) {
                templateId = $el.data("product-template-id");
            }
            var productReady = this.selectOrCreateProduct($el.closest("form"), productID, templateId, false);

            var line_id = parseInt($el.data("line-id"), 10);

            productReady.then(function (productId) {
                productId = parseInt(productId, 10);

                if (productId && $quantity_available >= parseFloat($el.closest("form").find(".quantity").val())) {
                    return self
                        ._rpc({
                            route: "/shop/cart/update_json",
                            params: {
                                product_id: productId,
                                line_id: line_id,
                                add_qty: $el.closest("form").find(".quantity").val() || 1.0,
                            },
                        })
                        .then(function (data) {
                            var $q = $(".my_cart_quantity");
                            if ($quantity_available >= data.quantity) {
                            }else{
                                console.log(parseFloat(data.quantity - $quantity_available))
                                self._rpc({
                                    route: "/shop/cart/update_json",
                                    params: {
                                        product_id: productId,
                                        line_id: line_id,
                                        add_qty: parseFloat(data.quantity - $quantity_available)*-1 || -1.0,
                                    },
                                })
                                $form.find(".sh_add_cart").prop("invisible", true).addClass('invisible').attr('invisible', 'invisible');
                            }
                            if (data.quantity){
                                $q.parents("li:first").removeClass("d-none");
                                $(".o_wsale_my_cart").show();
                                $(".my_cart_quantity").text(data.cart_quantity);
                                wSaleUtils.animateClone($(".o_wsale_my_cart"), $el.closest("form"), 20, 10);
                            }
                            if(data.warning){
                                $form.find(".sh_add_cart").prop("invisible", true).addClass('invisible').attr('invisible', 'invisible');
                            }
                        });
                }
                else{
                    console.log("añadiste más de la cuenta")
                    return self
                        ._rpc({
                            route: "/shop/cart/update_json",
                            params: {
                                product_id: productId,
                                line_id: line_id,
                                add_qty: 1,
                            },
                        })
                        .then(function (data) {
                            var $q = $(".my_cart_quantity");
                            console.log("añadí uno")
                            self._rpc({
                                route: "/shop/cart/update_json",
                                params: {
                                    product_id: productId,
                                    line_id: line_id,
                                    add_qty: -data.quantity,
                                },
                            })
                            console.log("quité todo")
                            self._rpc({
                                route: "/shop/cart/update_json",
                                params: {
                                    product_id: productId,
                                    line_id: line_id,
                                    add_qty: $quantity_available,
                                },
                            }).then(function (data) {
                                console.log("añadí la cantidad disponible")
                                $q.parents("li:first").removeClass("d-none");
                                $(".o_wsale_my_cart").show();
                                $(".my_cart_quantity").text(data.cart_quantity);
                                //console.log(data);
                                wSaleUtils.animateClone($(".o_wsale_my_cart"), $el.closest("form"), 20, 10);
                            });
                            $form.find(".sh_add_cart").prop("invisible", true).addClass('invisible').attr('invisible', 'invisible');
                        });
                }
            });
        },
    });
});
