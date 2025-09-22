
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class Meeting(models.Model):
    _inherit = 'calendar.event'

    @api.onchange('resource_ids')
    def _onchange_resource_ids(self):
        for record in self:
            if record.resource_ids:
                resource_names = ", ".join(record.resource_ids.mapped("name"))
                base_name = record.name.split(" con (")[0] if record.name else ""
                record.name = f"{base_name} con ({resource_names})" if base_name else resource_names

    @api.model
    def create(self, vals):
        print("CREATE vals:", vals)
        resource_ids = []
        if 'resource_ids' in vals:
            print("CREATE resource_ids:", vals['resource_ids'])
            if (
                isinstance(vals['resource_ids'], list)
                and vals['resource_ids']
            ):
                if isinstance(vals['resource_ids'][0], (list, tuple)) and len(vals['resource_ids'][0]) > 2 and vals['resource_ids'][0][0] == 6:
                    resource_ids = vals['resource_ids'][0][2]
                elif isinstance(vals['resource_ids'][0], (list, tuple)) and vals['resource_ids'][0][0] == 4:
                    resource_ids = [cmd[1] for cmd in vals['resource_ids'] if cmd[0] == 4]
                elif isinstance(vals['resource_ids'][0], int):
                    resource_ids = vals['resource_ids']
        print("CREATE resource_ids final:", resource_ids)
        # Asegura que el nombre nunca sea False o vacío
        if not vals.get('name'):
            if resource_ids:
                resource_names = ", ".join(self.env['resource.resource'].browse(resource_ids).mapped('name'))
                vals['name'] = resource_names
            else:
                vals['name'] = 'Sin título'
        return super().create(vals)

    def write(self, vals):
        print("WRITE vals:", vals)
        resource_ids = []
        if 'resource_ids' in vals:
            print("WRITE resource_ids:", vals['resource_ids'])
            if (
                isinstance(vals['resource_ids'], list)
                and vals['resource_ids']
            ):
                if isinstance(vals['resource_ids'][0], (list, tuple)) and len(vals['resource_ids'][0]) > 2 and vals['resource_ids'][0][0] == 6:
                    resource_ids = vals['resource_ids'][0][2]
                elif isinstance(vals['resource_ids'][0], (list, tuple)) and vals['resource_ids'][0][0] == 4:
                    resource_ids = [cmd[1] for cmd in vals['resource_ids'] if cmd[0] == 4]
                elif isinstance(vals['resource_ids'][0], int):
                    resource_ids = vals['resource_ids']
        print("WRITE resource_ids final:", resource_ids)
        # Asegura que el nombre nunca sea False o vacío
        if not vals.get('name'):
            if resource_ids:
                resource_names = ", ".join(self.env['resource.resource'].browse(resource_ids).mapped('name'))
                vals['name'] = resource_names
            else:
                vals['name'] = 'Sin título'
        return super().write(vals)
