# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_hide_zero_stock = fields.Boolean(related = 'pos_config_id.hide_zero_stock', readonly=False)

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     pos_hide_zero_stock = self.env['ir.config_parameter'].sudo().get_param('pos_product_stock_info.pos_hide_zero_stock', default=False)
    #     res.update(
    #         pos_hide_zero_stock=pos_hide_zero_stock,
    #     )
    #     return res
    #
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     self.env['ir.config_parameter'].sudo().set_param('pos_product_stock_info.pos_hide_zero_stock', self.pos_hide_zero_stock or False)

