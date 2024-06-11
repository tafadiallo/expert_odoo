import json
import datetime
import math
import re
import warnings

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


###################################################################################################
#                       1er cas: l'ordre de fabrication ne depasse pas 17h
###################################################################################################

    def adjust_order_dates(self):
        ordre_fabrication = self.env['mrp.production'].search([('id','=',self.id)])
        if ordre_fabrication:
            dure_hour = sum(ordre_fabrication.workorder_ids.mapped('duration_expected')) / 60
            print(dure_hour)
            # une creation pour le jour ( j )ou on a confimer le devis
            if dure_hour <= 8.0:
                date_planned_start = ordre_fabrication.date_planned_start
                date = date_planned_start.date()
                date_planned_finished = f"{date} 17:00:00"
                ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
                    'date_planned_start': date_planned_start,
                    'date_planned_finished': date_planned_finished
                }) 
            #
            
            if dure_hour > 8.0:
                print("1111111111111111111111111111111")
                dure_restant = dure_hour - 8.0
                while(dure_restant > 0):
                    print("22222222222222222222222222222222222222")
                    date_planned_start = ordre_fabrication.date_planned_start
                    date = date_planned_start.date()
                    date_planned_finished = f"{date} 17:00:00"
                    ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
                        'date_planned_start': date_planned_start,
                        'date_planned_finished': date_planned_finished
                    }) 
                    print("3333333333333333333333333333")
                    self.env['mrp.production'].with_context(skip_adjust_order_dates=True).create({
                        'date_planned_start': "2024-06-07 08:00:00",
                        'date_planned_finished': "2024-06-07 17:00:00",
                        'company_id': 1,
                        'consumption': 'flexible',
                        'location_dest_id': 1,
                        'location_src_id': 1,
                        'product_id': 1,
                        'product_uom_id': 1
                    })
                    dure_restant = dure_restant - 8.0

                # dure_restant < 0
                print("5555555555555555555555555")
                date_planned_start = ordre_fabrication.date_planned_start
                date = date_planned_start.date()
                date_planned_finished = f"{date} 17:00:00"
                ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
                    'date_planned_start': date_planned_start,
                    'date_planned_finished': date_planned_finished
                }) 
            
    @api.model
    def create(self, vals):
        res = super(MrpProduction, self).create(vals)
        # res.adjust_order_dates()
        return res
    

    def _plan_workorders(self, replan=False):
        print("333333333")
        self.ensure_one()

        if not self.workorder_ids:
            return

        work_hours_end = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(17, 0, 0))

        qty_to_produce = max(self.product_qty - self.qty_produced, 0)
        qty_to_produce = self.product_uom_id._compute_quantity(qty_to_produce, self.product_id.uom_id)

        start_date = max(self.date_planned_start, datetime.datetime.now())
        if replan:
            workorder_ids = self.workorder_ids.filtered(lambda wo: wo.state in ('pending', 'waiting', 'ready'))
            workorder_ids.leave_id.unlink()
        else:
            workorder_ids = self.workorder_ids.filtered(lambda wo: not wo.date_planned_start)

        dure_restant = 1000.0-8.0
        while(dure_restant > 0):
            # duration_expected = min(dure_restant, 1000)  # Durée maximale d'un ordre de travail
            best_finished_date = datetime.datetime.max
            vals = {}
            for workorder in workorder_ids:
                workcenters = workorder.workcenter_id | workorder.workcenter_id.alternative_workcenter_ids

                for workcenter in workcenters:
                    from_date, to_date = workcenter._get_first_available_slot(start_date, dure_restant)

                    if not from_date:
                        continue

                    if to_date.time() > work_hours_end.time():
                        to_date = datetime.datetime.combine(to_date.date(), work_hours_end.time())

                    if to_date < best_finished_date:
                        best_start_date = from_date
                        best_finished_date = to_date
                        best_workcenter = workcenter
                        vals = {
                            'workcenter_id': workcenter.id,
                            'duration_expected': dure_restant,
                        }

            if best_finished_date == datetime.datetime.max:
                raise UserError(_('Impossible to plan the workorder. Please check the workcenter availabilities.'))

            leave_end_time = work_hours_end.time() if best_finished_date.date() == start_date.date() else datetime.time(17, 0, 0)

            if best_finished_date.time() == leave_end_time:
                start_date = datetime.datetime.combine(start_date.date() + datetime.timedelta(days=1), datetime.time(8, 0, 0))  # Start time assuming 8 AM
                continue

            leave = self.env['resource.calendar.leaves'].create({
                'name': workorder.display_name,
                'calendar_id': best_workcenter.resource_calendar_id.id,
                'date_from': best_start_date,
                'date_to': best_finished_date,
                'resource_id': best_workcenter.resource_id.id,
                'time_type': 'other'
            })
            vals['leave_id'] = leave.id
            workorder.write(vals)

            dure_restant = dure_restant - 8.0

        self.with_context(force_date=True).write({
            'date_planned_start': self.workorder_ids[0].date_planned_start,
            'date_planned_finished': self.workorder_ids[-1].date_planned_finished
        })


####################################################################################################

















###################################################################################################
#                       1er cas_amelioration: l'ordre de fabrication ne depasse pas 17h 
###################################################################################################

    
    # def adjust_order_dates(self):
    #     ordre_fabrication = self.env['mrp.production'].browse(self.id)
    #     if ordre_fabrication:
    #         date_planned_start = "2024-06-02 08:00:00"
    #         date_planned_finished = "2024-06-02 17:00:00"

    #         ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
    #             'date_planned_start': date_planned_start,
    #             'date_planned_finished': date_planned_finished
    #         })

    #         # Assurez-vous que les IDs existent
    #         product = self.env['product.product'].browse(1)
    #         uom = self.env['uom.uom'].browse(1)
    #         location_dest = self.env['stock.location'].browse(1)
    #         location_src = self.env['stock.location'].browse(1)
    #         company = self.env.user.company_id

    #         if not product.exists() or not uom.exists() or not location_dest.exists() or not location_src.exists() or not company:
    #             raise ValidationError("Un des enregistrements référencés n'existe pas.")

    #         # Créez les deux enregistrements
    #         self.env['mrp.production'].with_context(skip_adjust_order_dates=True).create({
    #             'name': 'mounzo____',
    #             'date_planned_start': "2024-06-03 08:00:00",
    #             'date_planned_finished': "2024-06-03 17:00:00",
    #             'company_id': company.id,
    #             'consumption': 'flexible',
    #             'location_dest_id': location_dest.id,
    #             'location_src_id': location_src.id,
    #             'product_id': product.id,
    #             'product_uom_id': uom.id,
    #         })

    #         self.env['mrp.production'].with_context(skip_adjust_order_dates=True).create({
    #             'name': 'mounzo1àààààà',
    #             'date_planned_start': "2024-06-04 08:00:00",
    #             'date_planned_finished': "2024-06-04 17:00:00",
    #             'company_id': company.id,
    #             'consumption': 'flexible',
    #             'location_dest_id': location_dest.id,
    #             'location_src_id': location_src.id,
    #             'product_id': product.id,
    #             'product_uom_id': uom.id
    #         })


    # @api.model
    # def create(self, vals):
    #     res = super(MrpProduction, self).create(vals)
    #     if not self.env.context.get('skip_adjust_order_dates'):
    #         res.with_context(skip_adjust_order_dates=True).adjust_order_dates()
    #     return res
    
    
    # def unlink(self):
    #     for record in self:
    #         # Supprimer les messages liés
    #         mail_messages = self.env['mail.message'].search([])
    #         if mail_messages:
    #             for m in mail_messages:
    #                 m.unlink()
                
    #             print(f"User #{self.env.uid} deleted mail.message records linked to mrp.production ID {record.id}")

    #         # Supprimer les abonnés liés
    #         mail_followers = self.env['mail.followers'].search([])
    #         if mail_followers:
    #             for m in mail_followers:
    #                 m.unlink()
    #             print(f"User #{self.env.uid} deleted mail.followers records linked to mrp.production ID {record.id}")

    #         print(f"User #{self.env.uid} deleted mrp.production record with ID {record.id}")

    #     return super(MrpProduction, self).unlink()



####################################################################################################
