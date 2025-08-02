/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { browser } from "@web/core/browser/browser";

patch(ReceiptScreen.prototype, {
    orderDone() {
        this.pos.removeOrder(this.currentOrder);
        this._addNewOrder();
        this.pos.resetProductScreenSearch();
        browser.location.reload();
    }
});
