/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    /**
     * Override createNewOrder to automatically assign the default partner
     * defined in the POS config to every new order.
     *
     * In Odoo 18, this.config.default_partner_id is already resolved to a
     * res.partner record by the related-models system (as long as the partner
     * is included in the POS partner loading domain, which we guarantee in
     * models/pos_config.py via the _load_pos_data_domain override).
     */
    createNewOrder(data = {}) {
        const order = super.createNewOrder(data);

        const defaultPartner = this.config.default_partner_id;
        if (defaultPartner && !order.partner_id) {
            order.set_partner(defaultPartner);
        }

        return order;
    },
});
