# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from datetime import date
import logging
_logger = logging.getLogger(__name__)
class Order(models.Model):
    _inherit = "sale.order"
    
    date_order = fields.Datetime(
    string='Order Date',
    required=True,
    readonly=True,
    index=True,
    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},  # Added 'sale' state
    copy=False,
    default=fields.Datetime.now,
    help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders."
    )
     
    state_fabrik = fields.Boolean(default=False)

    @api.depends('order_line.purchase_line_ids.order_id')
    def _compute_purchase_order_count(self):
        for order in self:
            if order.name:
                achat = self.env['purchase.order'].search([('origin', '=',order.name)])
                if achat:
                    achat.project_client_tags = order.partner_id
            order.purchase_order_count = len(order._get_purchase_orders())

        
    def action_view_purchase_order(self):
         return  {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'name': _("Purchase Order generated from %s"),
            #'domain': [('id', 'in', purchase_order_ids)],
            'view_mode': 'tree,form',
        }
    

    def action_confirm(self):
        res = super(Order, self).action_confirm()
        nbre=0
        order = self.env['sale.order'].search([('name','=',self.name)])
        for line in self.order_line:
           if line.product_template_id and line.product_template_id.route_ids:
               for route in line.product_template_id.route_ids:
                   if route.name in ('Produire','Réapprovisionner sur commande (MTO)'):
                       nomenclature = self.env['mrp.bom'].search([('product_tmpl_id','=', line.product_template_id.id)])
                       if nomenclature and nomenclature.bom_line_ids:
                           print(" nomenclature",nomenclature)
                           for product in nomenclature.bom_line_ids:
                              nbre+=1
                              supplier = product.product_id.seller_ids and product.product_id.seller_ids[0].name or False
                             
                              purchase_order = self.env['purchase.order'].create({
                                    'partner_id': supplier,  
                                    'origin': self.name,
                              })
                             
                              self.env['purchase.order.line'].create({
                                'order_id': purchase_order.id,
                                'product_id': product.product_id.id,
                                'name': product.product_id.name,
                                'product_qty': line.product_uom_qty * product.product_qty,
                                'price_unit': 40000, 
                            })
        order.write({'purchase_order_count':nbre })
        _logger.info('#########################') 
        _logger.info(self.purchase_order_count) 
        _logger.info(order.purchase_order_count) 
        _logger.info('TTTTTTTTTTTTTTTTTTTTTTTTT')  
        self.state_fabrik=True                 
        return res
            


class Task(models.Model):
    _inherit = "project.task"
    
    employe_id = fields.Many2one('hr.employee', string="Employes")
    date_livraison = fields.Datetime(string="Date de livraison")
    commande = fields.Many2one('sale.order',string='Commande')



    @api.onchange('commande')
    def get_date_client(self):
        if self.commande:
            self.date_livraison, self.partner_id = self.commande.commitment_date, self.commande.partner_id

    
