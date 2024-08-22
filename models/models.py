from odoo import models, fields, api , _
from datetime import datetime
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools import format_datetime


class Attendance(models.Model):

    _inherit = 'hr.attendance'

    def custom_check_in_out(self):
        employee = self.env['hr.employee'].search([('id', '=', self.id)], limit=1)
        if employee:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_date = datetime.now().strftime('%Y-%m-%d')

            # current_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S') #02/11/2023 15:12:12
            last_attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id),('check_in', '<=', current_time)], order='id desc',
                                                               limit=1)
            if last_attendance:
                last_date = last_attendance.check_in.strftime('%Y-%m-%d')
                if current_date != last_date:
                    self.env['hr.attendance'].create({
                        'employee_id': employee.id,
                        'check_in': current_time,
                    })
                    return
            else:
                self.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': current_time,
                })
                return

            if last_attendance and last_attendance.check_out == False:
                last_attendance.write({'check_out': current_time})
                return
            else:
                if last_attendance and last_attendance.check_out and str(last_attendance.check_out) < current_time:
                    raise ValidationError(
                        _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                            'empl_name': employee.name,
                            'datetime': format_datetime(self.env, current_time, dt_format=False),
                        })


