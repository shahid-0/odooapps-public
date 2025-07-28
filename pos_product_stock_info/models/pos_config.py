from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_zero_stock = fields.Boolean("Hide Zero Stock")
