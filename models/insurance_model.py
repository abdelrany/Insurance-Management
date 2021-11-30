

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class InsuranceDetails(models.Model):
    _name = 'insurance.details'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_start = fields.Date(string='Date Started', default=fields.Date.today(), required=True)
    close_date = fields.Date(string='Date Closed')
    invoice_ids = fields.One2many('account.move', 'insurance_id', string='Invoices', readonly=True)
    commission_rate = fields.Float(string='Commission Percentage')
    policy_id = fields.Many2one('policy.details', string='Policy', required=True)
    amount = fields.Float(related='policy_id.amount', string='Amount')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('closed', 'Closed')],
                             required=True, default='draft')
    hide_inv_button = fields.Boolean(copy=False)
    note_field = fields.Html(string='Comment')


    def confirm_insurance(self):
        if self.amount > 0:
            self.state = 'confirmed'
            self.hide_inv_button = True
        else:
            raise UserError(_("Amount should be Greater than Zero"))


    def create_invoice(self):
        created_invoice=self.env['account.move'].create({
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': 'Invoice For Insurance',
                'quantity': 1,
                'price_unit': self.amount,
                'account_id': 41,
            })],
        })
        self.invoice_ids = created_invoice
        if self.policy_id.payment_type == 'fixed':
            self.hide_inv_button = False

    def close_insurance(self):
        for records in self.invoice_ids:
            if records.state == 'paid':
                raise UserError(_("All invoices must be Paid"))
        self.state = 'closed'
        self.hide_inv_button = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.details') or 'New'
        return super(InsuranceDetails, self).create(vals)

    @api.onchange('policy_id')
    def onchange_policy(self):
     for insurance in self:
        if insurance.policy_id:
            insurance.close_date = insurance.date_start + timedelta(days = insurance.policy_duration)
        else:

          insurance.close_date = 0




class AccountInvoiceRelate(models.Model):
    _inherit = 'account.move'

    insurance_id = fields.Many2one('insurance.details', string='Insurance')
