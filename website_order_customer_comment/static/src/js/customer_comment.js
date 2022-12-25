odoo.define('website_order_customer_comment.customer_comment', function (require) {
"use strict";
	var publicWidget = require('web.public.widget');

	publicWidget.registry.RentalProductSale = publicWidget.Widget.extend({
       selector: '.custom_customer_comment_probc',
       events: {
       	'click .submit_comment' : '_onCommentSaleOrder',
       },

       init: function () {
       this._super.apply(this, arguments);
            
       },
       start: function(){
       this._super.apply(this, arguments);
       $('#comment_blank_probc').hide()
       },
       _onCommentSaleOrder: function(ev){
       	var ajax = require('web.ajax');
        if($('#comment').val()){
       		ajax.jsonRpc("/custom_customer/comment", 'call', {
			'comment' : $('#comment').val(),
			'order_id':$('.hidden_id').val(),


		}).then(function (data){        

       			$(".custom_customer_comment_probc").load(location.href+" .custom_customer_comment_probc >*"," ")
       		})
       	  $("#customer_comment_probc").modal("hide");
       }else{
        $("#customer_comment_probc").modal("show");
        $('#comment_blank_probc').show()
        $('#comment_blank_probc').css("color", "red");
       }
       },
	});        
 });