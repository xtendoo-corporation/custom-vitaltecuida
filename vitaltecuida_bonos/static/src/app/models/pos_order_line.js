/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

const REMAINING_USES_NOTE_REGEX = /\s*[·-]?\s*Usos\s+restantes\s*:\s*\d+/i;
const PURCHASE_USES_NOTE_REGEX = /\s*[·-]?\s*Usos\s+del\s+bono\s*:\s*\d+\s*[→>-]+\s*\d+/i;

function getBalanceId(value) {
    if (Array.isArray(value)) {
        return value[0];
    }
    if (value && typeof value === "object") {
        return value.id;
    }
    return value || false;
}

function getBonoBaseName(line) {
    return (
        line._bono_product_display_name ||
        line.product_id?.display_name ||
        line.product_id?.name ||
        line.full_product_name ||
        _t("Bono sin nombre")
    );
}

function getBonoLineName(line) {
    const uses = Math.abs(Number(line.qty || 0)) || 1;
    return `${getBonoBaseName(line)} - ${uses} uso${uses !== 1 ? "s" : ""}`;
}

function getPartnerId(line) {
    return line.order_id?.partner_id?.id || line.order_id?.get_partner?.()?.id || false;
}

function getBonoBalance(line) {
    const balanceId = getBalanceId(line.bono_balance_id);
    const balances = line.models["vitaltecuida.bono.balance"];
    if (!balances) {
        return null;
    }
    if (balanceId) {
        return balances.find((balance) => balance.id === balanceId) || null;
    }
    const partnerId = getPartnerId(line);
    const productId = line.product_id?.id;
    if (!partnerId || !productId) {
        return null;
    }
    return balances.find(
        (balance) => balance.partner_id?.id === partnerId && balance.product_id?.id === productId
    );
}

function getLineBonoUsesDelta(line) {
    if (!line.product_id?.is_bono && !line.is_bono_redemption) {
        return 0;
    }
    if (line.is_bono_redemption) {
        return -Number(line.qty || 0);
    }
    return Number(line.qty || 0) * Number(line.product_id?.n_uses || 0);
}

function getRedemptionBaseNote(note = "") {
    const sanitizedNote = String(note || "").replace(REMAINING_USES_NOTE_REGEX, "").trim();
    return sanitizedNote || _t("Consumo de bono");
}

function getPurchaseBaseNote(note = "") {
    return String(note || "").replace(PURCHASE_USES_NOTE_REGEX, "").trim();
}

function hasRemainingUsesSummary(note = "") {
    return REMAINING_USES_NOTE_REGEX.test(String(note || ""));
}

function hasPurchaseUsesSummary(note = "") {
    return PURCHASE_USES_NOTE_REGEX.test(String(note || ""));
}

function updateRedemptionCustomerNote(line) {
    line.customer_note = getRedemptionBonoNote(line, getRedemptionBaseNote(line.customer_note));
}

function updatePurchaseCustomerNote(line) {
    line.customer_note = getPurchaseBonoNote(line, getPurchaseBaseNote(line.customer_note));
}

function getRedemptionBonoUsageInfo(line) {
    if (!line.is_bono_redemption || Number(line.qty || 0) <= 0) {
        return null;
    }
    const balance = getBonoBalance(line);
    if (!balance) {
        return null;
    }
    const orderLines = line.order_id?.lines || [];
    const currentIndex = orderLines.indexOf(line);
    const previousLines = currentIndex >= 0 ? orderLines.slice(0, currentIndex) : [];
    const previousPendingUses = previousLines
        .filter((otherLine) => otherLine.is_bono_redemption)
        .filter((otherLine) => isSameBonoBalance(line, otherLine))
        .reduce((acc, otherLine) => acc + Math.abs(Number(otherLine.qty || 0)), 0);
    const currentLineUses = Math.abs(Number(line.qty || 0)) || 1;
    return {
        remainingUses: Math.max(
            Number(balance.remaining_uses || 0) - previousPendingUses - currentLineUses,
            0
        ),
    };
}

function getPurchaseBonoUsageInfo(line) {
    if (line.is_bono_redemption || !line.product_id?.is_bono || Number(line.qty || 0) <= 0) {
        return null;
    }
    const orderLines = line.order_id?.lines || [];
    const currentIndex = orderLines.indexOf(line);
    const previousLines = currentIndex >= 0 ? orderLines.slice(0, currentIndex) : [];
    const previousUsesDelta = previousLines
        .filter((otherLine) => otherLine.product_id?.id === line.product_id?.id)
        .reduce((acc, otherLine) => acc + getLineBonoUsesDelta(otherLine), 0);
    const currentRemainingUses = Number(getBonoBalance(line)?.remaining_uses || 0);
    const beforeUses = currentRemainingUses + previousUsesDelta;
    const afterUses = beforeUses + getLineBonoUsesDelta(line);
    return {
        beforeUses,
        afterUses,
    };
}

function isSameBonoBalance(line, otherLine) {
    const lineBalanceId = getBalanceId(line.bono_balance_id);
    const otherBalanceId = getBalanceId(otherLine.bono_balance_id);
    if (lineBalanceId || otherBalanceId) {
        return lineBalanceId && lineBalanceId === otherBalanceId;
    }
    return otherLine.product_id?.id === line.product_id?.id;
}

function getRedemptionBonoNote(line, fallbackNote = "") {
    if (hasRemainingUsesSummary(fallbackNote)) {
        return fallbackNote;
    }
    const usageInfo = getRedemptionBonoUsageInfo(line);
    const baseNote = getRedemptionBaseNote(fallbackNote);
    if (!usageInfo) {
        return baseNote;
    }
    return `${baseNote} · ${_t("Usos restantes")}: ${usageInfo.remainingUses}`;
}

function getPurchaseBonoNote(line, fallbackNote = "") {
    if (hasPurchaseUsesSummary(fallbackNote)) {
        return fallbackNote;
    }
    const usageInfo = getPurchaseBonoUsageInfo(line);
    const baseNote = getPurchaseBaseNote(fallbackNote);
    if (!usageInfo) {
        return baseNote;
    }
    const summary = `${_t("Usos del bono")}: ${usageInfo.beforeUses} → ${usageInfo.afterUses}`;
    if (!baseNote) {
        return summary;
    }
    return `${baseNote} · ${summary}`;
}

patch(PosOrderline.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.is_bono_redemption = Boolean(vals.is_bono_redemption ?? this.is_bono_redemption);
        if (Object.prototype.hasOwnProperty.call(vals, "bono_balance_id")) {
            this.bono_balance_id = vals.bono_balance_id;
        }
        if (this.is_bono_redemption) {
            this.full_product_name = getBonoLineName(this);
            updateRedemptionCustomerNote(this);
        } else if (this.product_id?.is_bono) {
            updatePurchaseCustomerNote(this);
        }
    },

    set_quantity(quantity, keep_price) {
        const result = super.set_quantity(...arguments);
        if (this.is_bono_redemption) {
            this.full_product_name = getBonoLineName(this);
            updateRedemptionCustomerNote(this);
        } else if (this.product_id?.is_bono) {
            updatePurchaseCustomerNote(this);
        }
        return result;
    },

    can_be_merged_with(orderline) {
        if (this.is_bono_redemption || orderline.is_bono_redemption) {
            return false;
        }
        return super.can_be_merged_with(orderline);
    },

    get_customer_note() {
        const note = super.get_customer_note(...arguments) || "";
        if (this.is_bono_redemption) {
            if (hasRemainingUsesSummary(note)) {
                return note;
            }
            const redemptionNote = getRedemptionBonoNote(this, note);
            this.customer_note = redemptionNote;
            return redemptionNote;
        }
        if (this.product_id?.is_bono && hasPurchaseUsesSummary(note)) {
            return note;
        }
        const purchaseNote = getPurchaseBonoNote(this, note);
        if (this.product_id?.is_bono) {
            this.customer_note = purchaseNote;
        }
        return purchaseNote;
    },

    getDisplayData() {
        const data = super.getDisplayData();
        if (this.is_bono_redemption) {
            data.productName = getBonoLineName(this);
        }
        if (this.is_bono_redemption || this.product_id?.is_bono) {
            data.customerNote = this.get_customer_note();
        }
        return data;
    },
});
