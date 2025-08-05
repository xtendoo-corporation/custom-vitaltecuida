from odoo import models, fields, api


class ClientSessions(models.Model):
    _name = 'client.sessions'
    _description = 'Sesiones de Cliente'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Nombre de la Sesión',
        required=True,
        help='Nombre descriptivo de la sesión'
    )

    date = fields.Datetime(
        string='Fecha',
        required=True,
        default=fields.Datetime.now,
        help='Fecha y hora de la sesión'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade',
        help='Cliente asociado a esta sesión'
    )

    observations = fields.Text(
        string='Observaciones',
        help='Observaciones de la sesión'
    )

    extras = fields.Html(
        string='Extras',
        help='Información adicional en formato HTML'
    )

    @api.depends('name', 'date')
    def _compute_display_name(self):
        for record in self:
            if record.date:
                date_str = record.date.strftime('%d/%m/%Y %H:%M')
                record.display_name = f"{record.name} - {date_str}"
            else:
                record.display_name = record.name or 'Nueva Sesión'
