from odoo import api, models

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _load_pos_data_fields(self, config_id):
        res = super(ProductProduct, self)._load_pos_data_fields(config_id=config_id)

        res.append('qty_available')
        return res

    def _load_pos_data(self, data):
        res = super(ProductProduct, self)._load_pos_data(data=data)

        hide_zero_stock = self.env['ir.config_parameter'].get_param('pos_product_stock_info.hide_out_of_stock', default=False)
        res['hide_zero_stock'] = hide_zero_stock

        return res