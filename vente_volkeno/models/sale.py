# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class Order(models.Model):
    _inherit = "sale.order"
    _rec_name = "so_client"

    so_client = fields.Char(string="SO/Client",readonly=True, copy=False, index=True, compute='_so_client')
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
    state_achat = fields.Boolean(default=False)
    nbre_ids = fields.One2many('purchase.order','nbre_id')
    state_f = fields.Boolean(default=False)
    
    def write(self, vals):
        rec = super(Order, self).write(vals)

        date_livraison, partner_id = vals.get('commitment_date'), vals.get('partner_id')
        task_updates = {'date_livraison': date_livraison} if date_livraison else {}
        task_updates.update({'partner_id': partner_id}) if partner_id else {}

        if task_updates:
            tasck_order = self.env['project.task'].search([('commande', '=', self.id)])
            tasck_order.write(task_updates)
        return rec
    
   
    
    def _so_client(self):
        for rec in self:
            rec.so_client = rec.name + (' / ' + rec.partner_id.name if rec.name and rec.partner_id.name else '')


    def action_confirm(self):
        nbre = []
        res = super(Order, self).action_confirm()
        order = self.env['sale.order'].search([('name','=',self.name)])
        purchase_ids = self.env['purchase.order'].search([]).ids
        dict_supplier = {}
        vendors_by_purchase = {}
        supplier_purchases = {}  # Initialize an empty dictionary to store purchases per supplier

        for line in self.order_line:
            if line.product_template_id and line.product_template_id.detailed_type=='service':
                    _logger.info('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
                    self.state_achat = True
            if self.state_achat == True:
                    purchase_order_achat = self.env['purchase.order'].create({
                                'partner_id': line.product_template_id.seller_ids[0].name.id if line.product_template_id .seller_ids else 9,
                                'origin': self.name,
                                'project_client_tags':self.partner_id.id
                            })
                    _logger.info('lllllllllllllllllllllllllll')
                    _logger.info(purchase_order_achat)
                    _logger.info('^^^^^^^^^^^^^^^^^^^^^^^^^^')
       
                    nbre.append(purchase_order_achat.id)
                    
                    if purchase_order_achat:
                        produc_template = self.env['product.template'].search([('id','=',line.product_template_id.id)])
                        produc_product = self.env['product.product'].search([('name','=',produc_template.name)])
                        self.env['purchase.order.line'].create({
                                'order_id': purchase_order_achat.id,
                                'product_id': produc_product.id,
                                'name':line.product_template_id.name,
                                'product_qty': line.product_uom_qty,
                                'price_unit': line.product_template_id.list_price,
                            })
            if line.product_template_id and line.product_template_id.route_ids:
                for route in line.product_template_id.route_ids:
                    if route.name in ('Produire', 'Réapprovisionner sur commande (MTO)'):
                        self.state_fabrik = True
                    # if route.name in ('Acheter'):
                    #     self.state_achat = True
                        
                if  self.state_fabrik == True:
                    nomenclature = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_template_id.id)])
                    
                    if nomenclature and nomenclature.bom_line_ids:
                        for product in nomenclature.bom_line_ids:
                            
                            purchase_order = self.env['purchase.order'].create({
                                'partner_id': product.product_id.seller_ids[0].name.id,
                                'origin': self.name,
                                'project_client_tags':self.partner_id.id
                            })
                            
                            nbre.append(purchase_order.id)
                            
                            if purchase_order:
                                self.env['purchase.order.line'].create({
                                        'order_id': purchase_order.id,
                                        'product_id':  product.product_id.id,
                                        'name':product.product_id.name,
                                        'product_qty': line.product_uom_qty * product.product_qty,
                                        'price_unit': product.product_id.list_price,
                                    })
                            
        _logger.info('UUUUUUUUUUUUUUUUUUUUUUUUUU')  
        _logger.info(nbre)  
        _logger.info('UUUUUUUUUUUUUUUUUUUUUUUUUU')                 
        self.nbre_ids = nbre 
        return res
    
    def _get_purchase_orders(self):
        # global nbre
        _logger.info('#########################') 
        _logger.info(self.nbre_ids) 
        _logger.info('TTTTTTTTTTTTTTTTTTTTTTTTT')  
        for order in self:
            if self.nbre_ids:
                if order.order_line.product_template_id and order.order_line.product_template_id.route_ids:
                    for route in order.order_line.product_template_id.route_ids:
                        if route.name in ('Produire','Réapprovisionner sur commande (MTO)'):
                            for line in order.order_line:
                                nomenclature = self.env['mrp.bom'].search([('product_tmpl_id','=', line.product_template_id.id)])
                                if nomenclature and nomenclature.bom_line_ids:
                                    for product in nomenclature.bom_line_ids:  
                                        if product.product_id.route_ids:
                                            for  rout in  product.product_id.route_ids:
                                                if rout.name in ('Acheter'):
                                                    self.state_f = True
                        # if route.name == 'Acheter':
                        #     self.state_f = True
                if order.order_line :    
                    for service in order.order_line:
                        if service.product_template_id.detailed_type=='service':
                            _logger.info('TTTTTTTTTTTTTTTTTTTTTTTTT')
                            self.state_f = True
   
                if  self.state_f ==True:
                    return  self.nbre_ids


            else:
                return order.order_line.purchase_line_ids.order_id
        
            
    def action_view_purchase_orders(self):
        self.ensure_one()
        if not self.nbre_ids:
            purchase_order_ids = self._get_purchase_orders().ids  
            action = {
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
            }
            if len(purchase_order_ids) == 1:
                action.update({
                    'view_mode': 'form',
                    'res_id': purchase_order_ids[0],
                })
            else:
                action.update({
                    'name': _("Purchase Order generated from %s", self.name),
                    'domain': [('id', 'in', purchase_order_ids)],
                    'view_mode': 'tree,form',
                })
            return action
        else:
            purchase_order_ids =self.env['purchase.order'].search([('id','in',self.nbre_ids.ids)]).ids
            _logger.info('UUUUUUUUUUUUUUUUUU')
            _logger.info(purchase_order_ids)
            _logger.info('UUUUUUUUUUUUUUUUUU')
            action = {
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
            }
            if len(purchase_order_ids) == 1:
                action.update({
                    'view_mode': 'form',
                    'res_id': purchase_order_ids[0],
                })
            else:
                action.update({
                    'name': _("Purchase Order generated from %s", self.name),
                    'domain': [('id', 'in', purchase_order_ids)],
                    'view_mode': 'tree,form',
                })
            return action

class Task(models.Model):
    _inherit = "project.task"
    
    employe_id = fields.Many2one('hr.employee', string="Employes")
    date_livraison = fields.Datetime(string="Date de livraison")
    commande = fields.Many2one('sale.order',string='Commande')
    ref_client = fields.Char(related='commande.client_order_ref',string='Reference client')



    @api.onchange('commande')
    def get_date_client(self):
        if self.commande:
            self.date_livraison, self.partner_id = self.commande.commitment_date, self.commande.partner_id

# class Route(models.Model):
#     _inherit = "stock.location.route"
    
#     def archive_route(self):
#         routes = self.env['stock.location.route'].search([])
#         for route in routes:
#             if route.name not in ('Produire', 'Réapprovisionner sur commande (MTO)','Acheter'):
#                route.active = False