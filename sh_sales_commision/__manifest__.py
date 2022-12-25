# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Sales Commission",
    
    "author": "Softhealer Technologies",
    
    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",
        
    "version": "14.0.1",
    
    "license": "OPL-1",
    
    "category": "Sales",
    
    "summary": "Sales Commission By Margin,Sales Commission By Product Category, Sales Commission By Fix Price, Manage Sales Commission Module, Calculate Sales Commission, Count Sales Commission, Sales Commission By Sale Order, Sales Commission By Invoice Odoo",
        
    "description": """Do you want to manage the commission based on the sales order? Do you want to manage the commission based on the invoice? Do you want to manage the commission based on the payment? The commission will be calculated based on the conditions. You can calculate the commission by 3 ways,

1) Commission based on the sales order: When quotation is confirmed then commission of related sales manager is calculated.
2) Commission based on the invoice: When the invoice is validated then the commission of related sales manager is calculated.
3) Commission based on the payment: When the invoice is paid then the commission of related sales manager is calculated.
Commission types:  1) Standard Commission, 2) Partner Based Commission, 3) Product/ Product Category/ Margin Based Commission
You can print the sales commission analysis report of the salesperson between any date range. You can create the invoice for any commission. Sales Commission Management Odoo,Manage Sales Commission By Margin, Sales Commission By Product, Sales Commission By Product Category, Sales Commission By Fix Price, Manage Sales Commission Module, Calculate Sales Commission, Count Sales Commission, Sales Commission By Sale Order, Sales Commission By Invoice, Sales Commission By Payment Odoo, Sales Commission By Margin App, Sales Commission By Product, Sales Commission By Product Category, Sales Commission By Fix Price, Manage Sales Commission Module, Calculate Sales Commission, Count Sales Commission, Sales Commission By Sale Order, Sales Commission By Invoice, Sales Commission By Payment Odoo
""",
     
     
     
    "depends": ['sale_management','base','base_setup'],
    
    "data": [
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        'views/res_config.xml',
        'views/views.xml',
        'views/sales_commission_analysis.xml',
        "views/sale_view.xml",
        "views/invoice_view.xml",
        "wizard/create_inv_multi_action.xml",
        "report/report_sales_commission.xml",
        "report/sale_analysis_report_view.xml",
    ],    
    
    "images": ["static/description/background.png",],
                 
    "installable": True,
    "auto_install": False,
    "application": True,  
      
    "price": "60",
    "currency": "EUR"          
}
