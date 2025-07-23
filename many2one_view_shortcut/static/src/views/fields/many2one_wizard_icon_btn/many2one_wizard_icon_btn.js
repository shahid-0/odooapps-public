/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";

patch(Many2OneField.prototype, {
    async onExternalNewTabBtnClick(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        const action = await this.orm.call(this.relation, "get_formview_newtab_action", [[this.resId]], {
            context: this.context,
        });
        await this.action.doAction(action);
    },
    async onExternalWizardBtnClick(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        const action = await this.orm.call(this.relation, "get_wizardview_action", [[this.resId]], {
            context: this.context,
        });
        await this.action.doAction(action);
    }
})
