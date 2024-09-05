from odoo.exceptions import UserError, ValidationError
from odoo import api, models, fields

class Customer(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient')
    vat = fields.Char(string='Tax ID', required=True)

    @api.constrains('email', 'related_patient_id')
    def _check_email_in_patient(self):
        for record in self:
            if record.email:
                # Check if the email exists in the patient model
                patient = self.env['hms.patient'].search([('email', '=', record.email)], limit=1)
                if patient:
                    raise ValidationError(
                        f"The email '{record.email}' is already used by a patient ({patient.first_name})."
                    )
     
    @api.model
    def unlink(self):
        for record in self:
            if record.related_patient_id:
                raise UserError("You cannot delete a customer linked to a patient.")
        return super(Customer, self).unlink()