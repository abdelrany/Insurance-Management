

from odoo import models, fields


class PolicyDetails(models.Model):
    _name = 'policy.details'

    name = fields.Char(string='Name', required=True)
    policy_type = fields.Many2one('policy.type', string='Policy Type', required=True)
    payment_type = fields.Selection([('fixed', 'Fixed'), ('installment', 'Installment')],
                                    required=True, default='fixed')
    amount = fields.Float(string='Amount', required=True)
    policy_duration = fields.Integer(string='Duration in Days', required=True)
    note_field = fields.Html(string='Comment')


class PolicyType(models.Model):
    _name = 'policy.type'

    name = fields.Char(string='Name')
