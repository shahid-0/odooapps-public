from odoo import models, api

class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.model
    def get_erd_data(self, model_id):
        """
        Returns data for GoJS ERD diagram for the given model_id.
        Data structure:
        {
            'nodes': [
                {'key': 'res.partner', 'name': 'Contact', 'fields': [...]},
                {'key': 'res.users', 'name': 'User', 'fields': [...]},
                ...
            ],
            'links': [
                {'from': 'res.partner', 'to': 'res.users', 'text': 'user_id', 'toText': '1'},
                ...
            ]
        }
        """
        main_model = self.browse(model_id)
        if not main_model:
            return {'nodes': [], 'links': []}

        nodes = {}
        links = []
        
        # Helper to add node if not exists
        def add_node(model):
            if model.model not in nodes:
                field_list = []
                for field in model.field_id:
                    field_data = {
                        'name': field.name,
                        'type': field.ttype,
                        'required': field.required,
                        'string': field.field_description,
                    }
                    field_list.append(field_data)
                
                nodes[model.model] = {
                    'key': model.model,
                    'name': f"{model.name} ({model.model})",
                    'fields': field_list
                }

        # Add main model
        add_node(main_model)
        
        # Traverse fields to find relations
        # Limit depth to 1 for now to avoid huge diagrams
        # We can scan fields of the main model
        for field in main_model.field_id:
            if field.ttype in ['many2one', 'one2many', 'many2many'] and field.relation:
                related_model_name = field.relation
                related_model = self.search([('model', '=', related_model_name)], limit=1)
                
                if related_model:
                    add_node(related_model)
                    
                    # Create link
                    # from main to related
                    link_data = {
                        'from': main_model.model,
                        'to': related_model.model,
                        'text': field.name,
                        'toText': '1' if field.ttype == 'many2one' else 'N' # Simplified cardinality
                    }
                    links.append(link_data)

        return {
            'nodes': list(nodes.values()),
            'links': links
        }
