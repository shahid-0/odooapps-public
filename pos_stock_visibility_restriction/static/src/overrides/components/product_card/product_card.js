/* @odoo-module */

import { useEffect, useState } from "@odoo/owl";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ProductCard.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.qtyAvailable = useState({ value: this.pos.db.product_by_id[this.props.productId].qty_available });
    },
});





