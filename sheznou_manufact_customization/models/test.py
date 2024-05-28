from datetime import datetime, timedelta
import pytz
from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_ids = fields.One2many('res.partner', string="Clients", compute='_compute_sale_order_count')
    partner_id_custom = fields.Char(string='Clients', compute='_get_partner_ids', store=True)
    workorder_done = fields.Float(string="Progression", compute="_workorder_done")
    tache_name = fields.Char(string='Nom de la tâche')

    def adjust_order_dates(self):
        print("Adjusting order dates...")

        work_start = 8  # Heure de début (08h00)
        work_end = 17  # Heure de fin (17h00)
        work_days = [0, 1, 2, 3, 4]  # Jours ouvrés : Lundi (0) à Vendredi (4)
        tz = pytz.timezone(self.env.user.tz or 'UTC')  # Fuseau horaire de l'utilisateur

        def next_working_day(date):
            while date.weekday() not in work_days:
                date += timedelta(days=1)
            return date

        def next_working_hour(date):
            if date.hour < work_start:
                return date.replace(hour=work_start, minute=0)
            elif date.hour >= work_end:
                date = next_working_day(date + timedelta(days=1))
                return date.replace(hour=work_start, minute=0)
            return date

        orders = self.search([('state', 'not in', ['done', 'cancel'])])

        for order in orders:
            if not order.date_planned_start or not order.date_planned_finished:
                continue

            date_planned_start = order.date_planned_start.astimezone(tz)
            date_planned_finished = order.date_planned_finished.astimezone(tz)

            date_planned_start = next_working_hour(date_planned_start)
            duration = (date_planned_finished - date_planned_start).total_seconds() / 3600

            working_hours = work_end - work_start
            total_days = int(duration // working_hours)
            remaining_hours = duration % working_hours

            end_date = date_planned_start + timedelta(days=total_days)
            end_date = next_working_day(end_date)
            end_date = end_date.replace(hour=work_start + int(remaining_hours), minute=0)

            order.with_context(skip_adjust_order_dates=True).write({
                'date_planned_start': date_planned_start.astimezone(pytz.utc).replace(tzinfo=None),
                'date_planned_finished': end_date.astimezone(pytz.utc).replace(tzinfo=None),
            })

            dure_restant = 2000.0 - 8.0  # Exemple de durée restante
            if dure_restant > 0:
                self.create_additional_order(order, dure_restant)

    def create_additional_order(self, original_order, duration):
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        date_planned_start = datetime.now(tz).replace(hour=8, minute=0, second=0, microsecond=0)
        date_planned_start = self.next_working_hour(date_planned_start)

        work_start = 8
        work_end = 17
        working_hours = work_end - work_start
        total_days = int(duration // working_hours)
        remaining_hours = duration % working_hours

        end_date = date_planned_start + timedelta(days=total_days)
        end_date = self.next_working_day(end_date)
        end_date = end_date.replace(hour=work_start + int(remaining_hours), minute=0)

        self.create({
            'date_planned_start': date_planned_start.astimezone(pytz.utc).replace(tzinfo=None),
            'date_planned_finished': end_date.astimezone(pytz.utc).replace(tzinfo=None),
            'company_id': original_order.company_id.id,
            'consumption': original_order.consumption,
            'location_dest_id': original_order.location_dest_id.id,
            'location_src_id': original_order.location_src_id.id,
            'product_id': original_order.product_id.id,
            'product_uom_id': original_order.product_uom_id.id,
        })

    def next_working_day(self, date):
        work_days = [0, 1, 2, 3, 4]  # Jours ouvrés : Lundi (0) à Vendredi (4)
        while date.weekday() not in work_days:
            date += timedelta(days=1)
        return date

    def next_working_hour(self, date):
        work_start = 8  # Heure de début (08h00)
        work_end = 17  # Heure de fin (17h00)
        if date.hour < work_start:
            return date.replace(hour=work_start, minute=0)
        elif date.hour >= work_end:
            date = self.next_working_day(date + timedelta(days=1))
            return date.replace(hour=work_start, minute=0)
        return date

    @api.model
    def create(self, vals):
        print("Creating MRP Production...")
        res = super(MrpProduction, self).create(vals)
        if not self.env.context.get('skip_adjust_order_dates'):
            res.with_context(skip_adjust_order_dates=True).adjust_order_dates()
        return res

    def write(self, vals):
        print("Writing MRP Production...")
        if self.env.context.get('skip_adjust_order_dates'):
            return super(MrpProduction, self).write(vals)
        res = super(MrpProduction, self).write(vals)
        self.adjust_order_dates()
        return res
