# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Many2oneInherit(models.AbstractModel):
    _inherit = "base"

    def get_formview_newtab_action(self, access_uid=None):
        model_name = self._name
        record_id = self.id
        redirect_url = f"/web#id={record_id}&model={model_name}&view_type=form"
        return {
            'type': 'ir.actions.act_url',
            'url': redirect_url,
            'target': 'new',
        }

    def get_wizardview_action(self, access_uid=None):
        view_id = self.sudo().get_formview_id(access_uid=access_uid)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'views': [(view_id, 'form')],
            'target': 'new',
            'res_id': self.id,
            'context': dict(self._context),
        }


