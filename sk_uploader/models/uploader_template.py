from odoo import _, api, fields, models
from odoo.fields import Domain
from odoo.exceptions import ValidationError
from odoo.orm.identifiers import NewId


class UploaderTemplate(models.Model):
    _name = 'sk.uploader.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Uploader Template'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready_to_use', 'Ready to Use'),
    ], string='Status', default='draft')
    company_ids = fields.Many2many(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
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
        help="A unique field from mapping lines to check if record already exists in the database"
    )
    unique_field_id_domain = fields.Binary(
        "Unique Field Id Domain",
        help="This is the domain which will only show those unique fields which are the mapping fields of that template",
        compute="_compute_unique_field_id_domain"
    )
    parent_id = fields.Many2one('sk.uploader.template', 'Parent Location', index=True, check_company=True)
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

    @api.onchange("mapped_to")
    def _onchange_odoo_model_id(self):
        for rec in self:
            if rec.mapped_to:
                related_model_id = self.env["ir.model"].search([('model', '=', rec.mapped_to.relation)]).id
                rec.odoo_model_id = related_model_id
            else:
                rec.odoo_model_id = None

    @api.depends('field_mapping_lines')
    def _compute_unique_field_id_domain(self):
        """
        This method will return the domain for the unique fields
        """
        ids = [rec for rec in self.field_mapping_lines.mapped('id') if not isinstance(rec, NewId)]
        self.unique_field_id_domain = Domain([
            ('id', 'in', ids)
        ])

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
