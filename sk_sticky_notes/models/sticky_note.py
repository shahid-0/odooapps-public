from odoo import models, fields, api

class StickyNote(models.Model):
    _name = 'sticky.note'
    _description = 'Sticky Note'
    _order = 'create_date desc'

    name = fields.Char('Title', required=True, default='Untitled Note')
    text = fields.Text('Content')
    # color = fields.Selection([
    #     ('yellow', 'Yellow'),
    #     ('blue', 'Blue'),
    #     ('green', 'Green'),
    #     ('pink', 'Pink'),
    # ], string='Color', default='yellow')
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)

    active = fields.Boolean(default=True)
