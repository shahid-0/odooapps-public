from odoo import _, api, Command, models, fields
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlrd
from openpyxl import load_workbook
from odoo.tools.mimetypes import get_extension
import logging

# Set up logger
_logger = logging.getLogger(__name__)


class UploaderUploader(models.Model):
    _name = 'sk.uploader.uploader'
    _description = 'Uploader Uploader'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    uploader_file = fields.Binary("File")
    uploader_file_name = fields.Char("Filename")
    template_id = fields.Many2one("sk.uploader.template", "Template")
    batches = fields.Selection([
        ('10', '10'),
        ('50', '50'),
        ('100', '100'),
        ('custom', 'custom')
    ], "Batches", default='10')
    custom_batch = fields.Integer("Custom Batch", default=0)

    def upload_data(self):
        self.load_file()

    def load_file(self):
        """ Main function to load and process the uploaded file based on template mapping. """
        if not self.uploader_file:
            raise UserError("No file uploaded!")

        file_data = base64.b64decode(self.uploader_file)
        file_extension = get_extension(self.uploader_file_name)

        # Use BytesIO to create an in-memory file object
        file_io = BytesIO(file_data)

        try:
            # Load Excel file (supporting both xls and xlsx)
            if file_extension == '.xls':
                book = xlrd.open_workbook(file_contents=file_data)
                sheet = book.sheet_by_index(0)
                self._process_data(sheet, 'xls')
            elif file_extension == '.xlsx':
                wb = load_workbook(file_io)
                sheet = wb.active
                self._process_data(sheet, 'xlsx')
            else:
                raise UserError("Invalid file type. Please upload an Excel file (.xls or .xlsx).")

            return True
        except Exception as e:
            raise UserError(f"An error occurred: {str(e)}")

    def _process_data(self, sheet, file_type):
        """ Process Excel sheet and apply field mappings in batches. """
        # Get the headers (first row in the Excel sheet)
        headers = self._get_headers(sheet, file_type)

        # Get number of rows and columns in the sheet
        rows = sheet.nrows if file_type == 'xls' else sheet.max_row
        cols = sheet.ncols if file_type == 'xls' else sheet.max_column

        # Batch size (adjust this based on performance needs)
        batch_size = int(self.batches) if not self.batches == 'custom' else self.custom_batch
        row_batch = []

        total_rows = rows - 1  # excluding the header row
        if total_rows <= 0:
            raise UserError("The uploaded file does not contain any data rows to process.")
        processed_rows = 0

        for row_idx in range(1, rows):  # Skip header row
            # Read the row's values
            row_values = [sheet.cell(row_idx + 1, col_idx + 1).value for col_idx in
                          range(cols)] if file_type == 'xlsx' else [sheet.cell(row_idx, col_idx).value for col_idx in
                                                                    range(cols)]

            # Append the row values to the batch
            row_batch.append(row_values)

            # If batch size is reached, process the batch
            if len(row_batch) >= batch_size:
                self._process_rows(headers, row_batch)
                self.env.cr.commit()
                row_batch = []  # Reset the batch after processing
                processed_rows += batch_size

                _logger.info(f"Batch {processed_rows // batch_size} processed. Total processed: {processed_rows}/{total_rows}.")

        # Process any remaining rows in the last batch
        if row_batch:
            self._process_rows(headers, row_batch)
            processed_rows += len(row_batch)
            self.env.cr.commit()

            _logger.info(f"Remaining rows processed. Total processed: {processed_rows}/{total_rows}.")

        _logger.info("File import completed successfully. All batches processed.")

    def _get_headers(self, sheet, file_type):
        """ Get headers from the first row of the sheet. """
        if file_type == 'xls':
            headers = [sheet.cell(0, col_idx).value for col_idx in range(sheet.ncols)]
        elif file_type == 'xlsx':
            headers = [sheet.cell(row=1, column=col_idx + 1).value for col_idx in range(sheet.max_column)]
        return headers

    def _build_vals_from_template(self, template, headers, row_values):
        """
        Returns vals dict ready for ORM create()
        """
        unique_existing_recs = {}
        header_index = {h: i for i, h in enumerate(headers)}

        if template.duplicate_handling_policy in ["skip_duplicates", "update_duplicates"]:
            if not template.unique_field_id:
                raise ValidationError(f"Please select unique field on template '{template.name}' if you want to update or skip duplicates.")

            # Pre-process all unique records for better batch handling
            if template.unique_field_id.file_column not in header_index:
                raise UserError(f"Column {template.unique_field_id.file_column} not found in file.")
            unique_field_header_index = header_index[template.unique_field_id.file_column]
            unique_vals_to_search = {row[unique_field_header_index] for row in row_values}
            existing_recs_to_search = self.env[template.odoo_model_id.model].search(
                [(template.unique_field_id.odoo_field.name, 'in', list(unique_vals_to_search))]
            )

            # Map the unique values to their existing records
            unique_existing_recs = {
                getattr(rec, template.unique_field_id.odoo_field.name): rec
                for rec in existing_recs_to_search if getattr(rec, template.unique_field_id.odoo_field.name, False)
            }

            # if it's the main template and the user want to skip the duplicates then we will remove that rows from the file
            # and the reason I am removing it from here because I don't want to process uneccessary rows which I don;t want to create/update
            if template.duplicate_handling_policy == "skip_duplicates" and not template.parent_id:
                # Remove:
                # - rows that already exist in DB
                filtered_rows = []

                for row in row_values:
                    unique_val = row[unique_field_header_index]
                    if not unique_val:
                        continue
                    if unique_val in unique_existing_recs:
                        continue

                    filtered_rows.append(row)

                row_values = filtered_rows

        # Handle each row of values
        all_vals = []
        for row in row_values:
            row_vals = self._process_single_row(template, headers, row)
            all_vals.append(row_vals)

        return all_vals, unique_existing_recs

    def _process_single_row(self, template, headers, row):
        """
        Processes a single row of data and returns a dictionary of field mappings for ORM create()
        """
        vals = {}

        # Field mapping from template to row
        header_index = {h: i for i, h in enumerate(headers)}
        for mapping in template.field_mapping_lines:
            if mapping.file_column in header_index:
                vals[mapping.odoo_field.name] = row[header_index[mapping.file_column]]

        # Handle children
        for child in template.child_ids:
            child_vals, existing_recs = self._build_child_vals(child, headers, row)

            # child.mapped_to = Many2one field on THIS template
            odoo_field = child.mapped_to

            if odoo_field.ttype == 'one2many':
                vals.setdefault(odoo_field.name, []).append(Command.create(child_vals))

            elif odoo_field.ttype == 'many2one':
                related_record = self._handle_many2one(child, child_vals, existing_recs)
                vals[odoo_field.name] = related_record.id
            else:
                raise UserError(f"Unsupported relation field {odoo_field.name} ({odoo_field.type})")

        return vals

    def _build_child_vals(self, child, headers, row):
        """
        Handles processing for child records (one2many / many2one)
        """
        child_vals, existing_recs = self._build_vals_from_template(child, headers,[row])  # Process only the current row for child
        return child_vals, existing_recs

    def _handle_many2one(self, child, child_vals, existing_recs):
        """
        Manages the logic for handling Many2one relationships.
        Handles creating or updating related records as needed.
        """
        child_unique_field_name = child.unique_field_id.odoo_field.name
        existing_related_rec = existing_recs.get(child_vals[0].get(child_unique_field_name))

        if child.duplicate_handling_policy == "skip_duplicates" and existing_related_rec:
            return existing_related_rec
        elif child.duplicate_handling_policy == "update_duplicates" and existing_related_rec:
            existing_related_rec.write(child_vals[0])
            return existing_related_rec
        else:
            return self.env[child.mapped_to.relation].create(child_vals[0])

    def _process_rows(self, headers, row_values):
        vals, existing_recs = self._build_vals_from_template(
            self.template_id,
            headers,
            row_values
        )

        if self.template_id.duplicate_handling_policy == "update_duplicates" and existing_recs:
            unique_field = self.template_id.unique_field_id.odoo_field.name
            remaining_vals = []

            for val in vals:
                unique_value = val.get(unique_field)
                if unique_value and unique_value in existing_recs:
                    existing_rec = existing_recs.pop(unique_value)
                    existing_rec.write(val)
                    # do NOT add to remaining_vals → removed from create list
                else:
                    remaining_vals.append(val)

            vals = remaining_vals
            self.env[self.template_id.odoo_model_id.model].create(vals)
            return

        self.env[self.template_id.odoo_model_id.model].create(vals)

    @api.constrains('custom_batch')
    def _custom_batch_constraint(self):
        for rec in self:
            if rec.batches == 'custom' and rec.custom_batch < 1:
                raise ValidationError("Custom batch should should be greater than 0.")
