from odoo import api, fields, models

class UploaderFieldMapping(models.Model):
    _name = "sk.uploader.field.mapping"
    _description = "Uploader Field Mapping"
    _rec_name = "file_column"

    file_column = fields.Char("File Field", help="This is the column name from the file.")
    odoo_field = fields.Many2one(
        'ir.model.fields',
        string='Odoo Field'
    )
    uploader_template_id = fields.Many2one("sk.uploader.template", "Uploader Template")
    is_required_field = fields.Boolean("Is Required Field", compute="_compute_is_required_field")

    @api.depends('odoo_field')
    def _compute_is_required_field(self):
        for rec in self:
            rec.is_required_field = rec.odoo_field.required
