import datetime
from datetime import date
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    timesheet = fields.Many2many("account.analytic.line", string="Feuille de temps",domain="[('employee_id','=',employee_id)]")

    worked_hours_2 = fields.Float(string='Heures passées sur les tâches', compute='_compute_worked_hours_2', store=True, readonly=True)

   
    @api.depends('timesheet')
    def _compute_worked_hours_2(self):
        for wh2 in self: 
            if wh2.timesheet and wh2.employee_id:
                total_hours = 0.0
                for time in wh2.timesheet:
                    _logger.info("Unit Amount: %s", time.unit_amount)
                    total_hours += time.unit_amount
                wh2.worked_hours_2 = total_hours
            else:
                wh2.worked_hours_2 = 0.0
