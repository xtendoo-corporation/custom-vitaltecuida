# Copyright 2025 Vitaltecuida
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from collections import defaultdict


class PosSessionReportWizard(models.TransientModel):
    _name = 'pos.session.report.wizard'
    _description = 'Asistente para Informe Detallado de Sesiones POS'

    session_ids = fields.Many2many(
        'pos.session',
        string='Sesiones POS',
        required=True,
        help='Seleccione una o más sesiones para el informe'
    )

    date_from = fields.Datetime(
        string='Fecha Desde',
        help='Filtrar pedidos desde esta fecha'
    )

    date_to = fields.Datetime(
        string='Fecha Hasta',
        help='Filtrar pedidos hasta esta fecha'
    )

    report_type = fields.Selection([
        ('detailed', 'Detallado (por ticket)'),
        ('summary', 'Resumen'),
    ], string='Tipo de Informe', default='detailed', required=True)

    @api.model
    def default_get(self, fields_list):
        """Establecer sesiones por defecto desde el contexto"""
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'pos.session' and self.env.context.get('active_ids'):
            res['session_ids'] = [(6, 0, self.env.context.get('active_ids'))]
        return res

    def action_print_report(self):
        """Imprimir el informe PDF"""
        self.ensure_one()
        return self.env.ref('vitaltecuida_pos_reports.action_report_pos_session_detailed').report_action(self)

    def _get_report_data(self):
        """Preparar los datos para el informe"""
        self.ensure_one()

        # Dominio base para buscar pedidos
        domain = [
            ('session_id', 'in', self.session_ids.ids),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]

        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))

        # Obtener todos los pedidos
        orders = self.env['pos.order'].search(domain, order='date_order asc')

        # Agrupar por sesión
        sessions_data = []
        for session in self.session_ids.sorted(key=lambda s: s.start_at):
            session_orders = orders.filtered(lambda o: o.session_id == session)

            # Calcular totales de la sesión
            total_amount = sum(session_orders.mapped('amount_total'))
            total_tax = sum(session_orders.mapped('amount_tax'))

            # Agrupar por método de pago
            payment_summary = defaultdict(float)
            for order in session_orders:
                for payment in order.payment_ids:
                    payment_summary[payment.payment_method_id.name] += payment.amount

            # Agrupar por impuestos
            tax_summary = defaultdict(lambda: {'base': 0.0, 'amount': 0.0})
            for order in session_orders:
                for line in order.lines:
                    for tax in line.tax_ids:
                        tax_key = f"{tax.name} ({tax.amount}%)"
                        tax_amount = line.price_subtotal_incl - line.price_subtotal
                        tax_summary[tax_key]['base'] += line.price_subtotal
                        tax_summary[tax_key]['amount'] += tax_amount

            # Preparar datos de pedidos
            orders_data = []
            for order in session_orders:
                # Líneas del pedido
                lines_data = []
                for line in order.lines:
                    tax_amount = line.price_subtotal_incl - line.price_subtotal
                    lines_data.append({
                        'product': line.product_id.display_name,
                        'qty': line.qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'subtotal': line.price_subtotal,
                        'tax_amount': tax_amount,
                        'total': line.price_subtotal_incl,
                    })

                # Pagos del pedido
                payments_data = []
                for payment in order.payment_ids:
                    payments_data.append({
                        'method': payment.payment_method_id.name,
                        'amount': payment.amount,
                    })

                orders_data.append({
                    'name': order.name,
                    'pos_reference': order.pos_reference,
                    'date_order': order.date_order,
                    'user': order.user_id.name,
                    'partner': order.partner_id.name if order.partner_id else 'Cliente General',
                    'lines': lines_data,
                    'amount_subtotal': order.amount_total - order.amount_tax,
                    'amount_tax': order.amount_tax,
                    'amount_total': order.amount_total,
                    'payments': payments_data,
                })

            sessions_data.append({
                'session': session,
                'orders': orders_data,
                'total_orders': len(session_orders),
                'total_amount': total_amount,
                'total_tax': total_tax,
                'payment_summary': dict(payment_summary),
                'tax_summary': dict(tax_summary),
            })

        # Totales generales de todas las sesiones
        grand_total = sum(s['total_amount'] for s in sessions_data)
        grand_total_tax = sum(s['total_tax'] for s in sessions_data)
        grand_total_orders = sum(s['total_orders'] for s in sessions_data)

        # Resumen general de pagos
        grand_payment_summary = defaultdict(float)
        for session_data in sessions_data:
            for method, amount in session_data['payment_summary'].items():
                grand_payment_summary[method] += amount

        # Resumen general de impuestos
        grand_tax_summary = defaultdict(lambda: {'base': 0.0, 'amount': 0.0})
        for session_data in sessions_data:
            for tax_key, values in session_data['tax_summary'].items():
                grand_tax_summary[tax_key]['base'] += values['base']
                grand_tax_summary[tax_key]['amount'] += values['amount']

        return {
            'sessions_data': sessions_data,
            'grand_total': grand_total,
            'grand_total_tax': grand_total_tax,
            'grand_total_orders': grand_total_orders,
            'grand_payment_summary': dict(grand_payment_summary),
            'grand_tax_summary': dict(grand_tax_summary),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_type': self.report_type,
        }

