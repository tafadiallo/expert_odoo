
from odoo import models, api,fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    project_client_tags = fields.Many2one('res.partner', string='Client')
    
    @api.model
    def create(self, vals):
        # if vals.get('origin'):
        #     sale_order = self.env['sale.order'].search([('name', '=', vals.get('origin'))])
        #     if sale_order:
        #         vals['project_client_tags'] = sale_order.partner_id
        return super(PurchaseOrder, self).create(vals)

    def update_client_attach_po_so(self):
         pos = self.env['purchase.order'].search([])
         for po in pos:
            if po.origin:
                sale_order = self.env['sale.order'].search([('name', '=',po.origin)])
                if sale_order:
                    po.project_client_tags = sale_order.partner_id
                    
    def action_view_picking(self):
        if self.name:
            stock = self.env['stock.picking'].search([('origin', '=',self.name)])
            if stock and stock.move_line_ids_without_package:
                lots = self.env['stock.production.lot'].search([('product_id', '=', stock.move_line_ids_without_package.product_id.id)])
                stock.move_line_ids_without_package.lot_name = lots.name
        return self._get_action_view_picking(self.picking_ids)
    
  
# class Production(models.Model):
#     _inherit = 'repair.order'
    
#     employe_id = fields.Many2one('hr.employee', string='Employer')
    
  
class Outils(models.Model):
    _inherit='repair.order'
    
    # @api.model
    # def create(self, vals):
        # if vals.get('origin'):
        #     lots = self.env['stock.production.lot'].search([('product_id', '=', vals.get('origin'))])
        #     sale_order = self.env['sale.order'].search([('name', '=', vals.get('origin'))])
        #     if sale_order:
        #         vals['project_client_tags'] = sale_order.partner_id
        # if vals.get('origin'):
        #     purchase_order = self.env['purchase.order'].search([('name', '=', vals.get('origin'))])
        #     if purchase_order:
        #         if vals.get('move_line_ids_without_package'):
        #               line_stock = self.env['stock.move.line'].search([('id', '=',vals.get('move_line_ids_without_package'))])
        #               if line_stock :
        #                   lots = self.env['stock.production.lot'].search([('product_id', '=', line_stock.product_id)])
        #                   line_stock.lot_name = lots.name
        # res = super(StockPicking, self).create(vals)
        # return res