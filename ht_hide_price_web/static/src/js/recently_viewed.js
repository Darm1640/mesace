odoo.define('ht_hide_price_web.recently_viewed', function (require) {
'use strict';
var core = require('web.core');
var ajax = require('web.ajax');
var qweb = core.qweb;
ajax.loadXML('/ht_hide_price_web/static/src/xml/recently_viewed_inhe.xml', qweb);
	
});

