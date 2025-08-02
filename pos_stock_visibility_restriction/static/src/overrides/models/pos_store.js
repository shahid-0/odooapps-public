/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

patch(PosStore.prototype, {
    async addProductToCurrentOrder(product, options = {}) {
        if (this.config.restrict_zero_stock && product.qty_available <= 0) {
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: _t("Product Out of Stock"),
                body: _t("%s is out of stock. Click order, if you still want to add this product", product.display_name),
                confirmClass: "btn-primary",
                confirmText: _t("Order"),
                cancelText: _t("Cancel"),
            });
            debugger;
            if (confirmed) {
                await super.addProductToCurrentOrder(...arguments)
            } else {
                // Cancel backspace
                return;
            }
        } else {
            await super.addProductToCurrentOrder(...arguments);
        }

   }
});
