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

        current_date = fields.Date.today()
        current_time = datetime.now()

        existing_attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', current_date)  # Check if the check_in is today
        ], limit=1)

        # If an existing record is found, handle it
        if existing_attendance:
            if existing_attendance.check_out:
                raise ValidationError(
                    _("Employee %(empl_name)s has already checked out today.") % {
                        'empl_name': employee.name,
                    })
            else:
                # Update the existing attendance record with the current checkout time
                existing_attendance.write({'check_out': current_time})
                return  # Exit the method after updating

        # If no existing attendance record is found for today, check for a last check-in
        last_attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_out', '=', False)  # Ensure we find an active check-in
        ], order='id desc', limit=1)

        if not last_attendance:
            raise ValidationError(
                _("No active check-in found for employee %(empl_name)s") % {
                    'empl_name': employee.name,
                })

        # Update the last check-in record with the checkout time
        last_attendance.write({'check_out': current_time})
