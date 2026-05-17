from odoo import models, fields

class ExpenseExpense(models.Model):
    _name = 'expense.expense'
    _description = 'Expense Tracker'
    # This inheritance is what connects your module to the mail system
    _inherit = ['mail.thread']

    name = fields.Char(string='Description', required=True)
    spent_by = fields.Many2one('res.users', string='Spent By', default=lambda self: self.env.user)
    amount = fields.Float(string='Amount', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    category = fields.Selection([
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('utilities', 'Utilities'),
        ('other', 'Other')
    ], string='Category', default='other')

# The space below is intentionally added to help Docker notice the file update