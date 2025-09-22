/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CalendarFilterPanel } from "@web/views/calendar/filter_panel/calendar_filter_panel";

patch(CalendarFilterPanel.prototype, {
    getSortedFilters(section) {
        const filters = super.getSortedFilters(section);
        filters.forEach(f => {
            if (f.type === "user") {
                f.active = false; // Desmarca asistentes
            } else {
                f.active = true; // Marca los demás
            }
        });
        return filters;
    },
});
