import re
from odoo import exceptions, models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class Patient(models.Model):
    _name = 'hms.patient'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    birth_date = fields.Date(string='Birth Date')
    history = fields.Html(string='Medical History')
    cr_ratio = fields.Float(string='CR Ratio')
    blood_type = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'),
         ('ab+', 'AB+'), ('ab-', 'AB-'), ('o+', 'O+'), ('o-', 'O-')],
        string='Blood Type'
    )
    pcr = fields.Boolean(string='PCR Test', default=False)
    image = fields.Binary(string='Image')
    address = fields.Text(string='Address')
    email = fields.Char(string='Email', required=True, unique=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    department_id = fields.Many2one('hms.department', string='Department')
    department_capacity = fields.Integer(string='Department Capacity', related='department_id.capacity', readonly=True)
    doctor_ids = fields.Many2many('hms.doctor', readonly=True)
    log_ids = fields.One2many('hms.patient.log', 'patient_id', string='Log History', copy=False)
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], string='State', default='undetermined')

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                rec.age = relativedelta(fields.Date.today(), rec.birth_date).years
            else:
                rec.age = 0

    @api.constrains('pcr', 'cr_ratio')
    def _check_cr_ratio(self):
        for rec in self:
            if rec.pcr and not rec.cr_ratio:
                raise exceptions.ValidationError("CR Ratio is required when PCR is checked.")

    @api.onchange('birth_date')
    def _onchange_birth_date(self):
        if self.age < 30:
            if not self.pcr:
                self.pcr = True
                _logger.warning("PCR Test has been automatically checked as the age is below 30.")

    @api.constrains('department_id')
    def _check_department_closed(self):
        for record in self:
            if record.department_id and not record.department_id.is_opened:
                raise exceptions.ValidationError("The selected department is closed and cannot be used.")
    @api.constrains('email')
    def _check_valid_email(self):
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        for record in self:
            if record.email and not re.match(email_pattern, record.email):
                raise exceptions.ValidationError("The email address is not valid.")

    @api.model
    def create(self, vals):
        _logger.info(f"Creating record with vals: {vals}")
        if 'department_id' in vals:
            department = self.env['hms.department'].browse(vals['department_id'])
            if department and not department.is_opened:
                raise exceptions.ValidationError("The selected department is closed and cannot be used.")
        record = super(Patient, self).create(vals)
        if 'state' in vals:
            _logger.info(f"State provided: {vals['state']}")
            self._create_state_change_log(record, vals['state'])
        return record

    def write(self, vals):
        old_states = {rec.id: rec.state for rec in self}

        department = None
        if 'department_id' in vals:
            department = self.env['hms.department'].browse(vals['department_id'])
            if department and not department.is_opened:
                raise exceptions.ValidationError("The selected department is closed and cannot be used.")

        res = super(Patient, self).write(vals)
        if 'state' in vals:
            new_state = vals['state']
            for record in self:
                old_state = old_states.get(record.id)
                if old_state != new_state:
                    self._create_state_change_log(record, new_state)

        return res

    def _create_state_change_log(self, record, new_state):
        _logger.info(f"Creating log for state change: {new_state}")
        description = f"State changed to {new_state.capitalize()}"
        _logger.info(f"Description: {description}")
        self.env['hms.patient.log'].create({
            'patient_id': record.id,
            'description': description,
            'created_by': self.env.user.id,
            'date': fields.Date.today(),
        })

class PatientLog(models.Model):
    _name = 'hms.patient.log'
    _description = 'Patient Log History'

    patient_id = fields.Many2one('hms.patient')
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user, readonly=True)
    date = fields.Date(string='Date', default=fields.Date.today, readonly=True)
    description = fields.Text(string='Description')
