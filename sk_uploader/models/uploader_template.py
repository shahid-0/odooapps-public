from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.api import NewId


class UploaderTemplate(models.Model):
    _name = 'sk.uploader.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Uploader Template'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    company_ids = fields.Many2many(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    unique_field = fields.Char(
        string="Unique Field (Excel Column)",
        help="Excel column name used to check existing records"
    )
    odoo_model_id = fields.Many2one("ir.model", "Odoo Model")
    field_mapping_lines = fields.One2many(
        'sk.uploader.field.mapping',
        'uploader_template_id',
        string="Field Mapping Lines",
        copy=True
    )
    unique_field_id = fields.Many2one(
        'sk.uploader.field.mapping',
        'Unique Field',
        compute='_compute_unique_field',
        store=True,
        help="A unique field from mapping lines to check if record already exists in the database"
    )
    unique_field_id_domain = fields.Binary(
        "Unique Field Id Domain",
        help="This is the domain which will only show those unique fields which are the mapping fields of that template",
        compute="_compute_unique_field_id_domain"
    )
    parent_id = fields.Many2one('sk.uploader.template', 'Parent Location', index=True, check_company=True, ondelete='cascade')
    child_ids = fields.One2many('sk.uploader.template', 'parent_id', 'Sub-Templates')
    parent_odoo_model_id = fields.Integer(
        related="parent_id.odoo_model_id.id",
        string="Parent Odoo Model Id",
        help="This field will be used for the mapped_to field as a domain"
    )
    mapped_to = fields.Many2one(
        'ir.model.fields',
        "Mapped To",
        help="This field will only show on subtemplates and it means that every time we create a record of subtemplate should be assigned to this field of parent template"
    )

    duplicate_handling_policy = fields.Selection([
        ('always_create', 'Always Create'),
        ('update_duplicates', 'Update Duplicates'),
        ('skip_duplicates', 'Skip Duplicates'),
    ], "Duplicate Handling Action", default="skip_duplicates")

    @api.depends('unique_field')
    def _compute_unique_field(self):
        for record in self:
            record.unique_field_id = False

            if not record.unique_field:
                return

            mapping_line = record.field_mapping_lines.filtered(
                lambda l: l.file_column == record.unique_field
            )

            if not mapping_line:
                raise UserError(
                    f"Column '{record.unique_field}' does not exist in Field Mapping Lines."
                )

            record.unique_field_id = mapping_line[0].ids[0]

    @api.depends('field_mapping_lines')
    def _compute_unique_field_id_domain(self):
        """
        This method will return the domain for the unique fields
        """
        ids = [rec for rec in self.field_mapping_lines.mapped('id') if not isinstance(rec, NewId)]
        self.unique_field_id_domain = [('id', 'in', ids)]

    @api.constrains('duplicate_handling_policy', 'parent_id')
    def _check_duplicate_policy_with_parent(self):
        for rec in self:
            if rec.parent_id and rec.duplicate_handling_policy == 'always_create':
                raise ValidationError(
                    _(
                        """“‘Always Create’ is not allowed for sub-templates. 
                        Use ‘Update Duplicates’ to update and link an existing record (or create it if it does not exist), 
                        or use ‘Skip Duplicates’ to link the existing record and create a new one only if it does not already exist.”"""
                    )
                )
