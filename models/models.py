from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime

class Attendance(models.Model):
    _inherit = 'hr.attendance'

    def custom_check_in(self):
        employee = self.env['hr.employee'].search([('id', '=', self.id)], limit=1)
        if not employee:
            raise ValidationError(_("Employee not found."))

        current_date = datetime.now().date()

        # Check if the employee has already checked in today
        today_check_in = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', datetime.combine(current_date, datetime.min.time())),
            ('check_in', '<=', datetime.combine(current_date, datetime.max.time()))
        ], limit=1)
        print(today_check_in,"eeeeeeeeeeeeeeeeeeetoday_check_ineeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        if  today_check_in:
            raise ValidationError(
                _("The employee %(empl_name)s is checked in today at %(datetime)s") % {
                    'empl_name': employee.name,
                    'datetime': format_datetime(self.env, today_check_in.check_in, dt_format=False),
                })

        # Create new check-in record
        self.env['hr.attendance'].create({
            'employee_id': employee.id,
            'check_in': datetime.now(),
        })

    def custom_check_out(self):
        employee = self.env['hr.employee'].search([('id', '=', self.id)], limit=1)
        if not employee:
            raise ValidationError(_("Employee not found."))

        current_time = datetime.now()

        # Find the last attendance record where the employee has checked in but not yet checked out
        last_attendance = self.env['hr.attendance'].search(
            [('employee_id', '=', employee.id), ('check_out', '=', False)],
            order='id desc',
            limit=1
        )
        print(last_attendance,"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        if not last_attendance and  last_attendance.check_out != False :
            raise ValidationError(
                _("No active check-in found for employee %(empl_name)s") % {
                    'empl_name': employee.name,
                })

        last_attendance.write({'check_out': current_time})
