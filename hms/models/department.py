from odoo import models, fields, api



class Department(models.Model):
    _name = 'hms.department'


    name=fields.Char(string='Name', required=True)
    capacity=fields.Integer(string='Capacity')
    is_opened=fields.Boolean(string='Is_opened', required=True)
    patient_ids=fields.One2many('hms.patient', 'department_id', string='Patients')




