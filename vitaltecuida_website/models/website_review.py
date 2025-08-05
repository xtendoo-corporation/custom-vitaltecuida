from odoo import models, fields, api
from datetime import datetime


class WebsiteReview(models.Model):
    _name = 'website.review'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Reseñas del sitio web de Vitaltecuida'
    _order = 'create_date desc'
    _rec_name = 'customer_name'

    customer_name = fields.Char(string='Nombre', required=True, help='Nombre del cliente que deja la reseña')
    email = fields.Char(string='Email', help='Email del cliente (opcional)')
    rating = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    ], string='Calificación', required=True, default='5')

    title = fields.Char(string='Título de la reseña', required=True, help='Título breve de la experiencia')
    review_text = fields.Text(string='Comentario', required=True, help='Detalle de la experiencia con Vitaltecuida')

    # Estados de moderación
    state = fields.Selection([
        ('pending', 'Pendiente de Revisión'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ], string='Estado', default='pending', required=True)

    # Campos de moderación
    moderated_by = fields.Many2one('res.users', string='Moderado por', readonly=True)
    moderation_date = fields.Datetime(string='Fecha de moderación', readonly=True)
    rejection_reason = fields.Text(string='Razón del rechazo', help='Motivo por el cual se rechazó la reseña')

    # Campos técnicos
    website_published = fields.Boolean(string='Publicado en web', default=False,
                                     help='Si está marcado, la reseña se muestra en el sitio web')
    ip_address = fields.Char(string='Dirección IP', help='IP desde donde se envió la reseña')
    user_agent = fields.Text(string='User Agent', help='Navegador usado para enviar la reseña')

    @api.model
    def create(self, vals):
        """
        Al crear una reseña, establecer automáticamente como pendiente
        """
        vals['state'] = 'pending'
        vals['website_published'] = False
        return super().create(vals)

    def action_approve(self):
        """
        Aprobar la reseña para mostrarla en el sitio web
        """
        for record in self:
            record.write({
                'state': 'approved',
                'website_published': True,
                'moderated_by': self.env.user.id,
                'moderation_date': datetime.now(),
                'rejection_reason': False,
            })

    def action_reject(self):
        """
        Rechazar la reseña
        """
        for record in self:
            record.write({
                'state': 'rejected',
                'website_published': False,
                'moderated_by': self.env.user.id,
                'moderation_date': datetime.now(),
            })

    def action_reset_to_pending(self):
        """
        Volver la reseña a estado pendiente
        """
        for record in self:
            record.write({
                'state': 'pending',
                'website_published': False,
                'moderated_by': False,
                'moderation_date': False,
                'rejection_reason': False,
            })

    @api.model
    def get_published_reviews(self, limit=10):
        """
        Obtener reseñas aprobadas para mostrar en el sitio web
        """
        return self.search([
            ('state', '=', 'approved'),
            ('website_published', '=', True),
        ], limit=limit, order='create_date desc')

    def get_rating_stars_html(self):
        """
        Obtener HTML con estrellas para mostrar la calificación
        """
        rating_int = int(self.rating)
        stars_html = '⭐' * rating_int
        return stars_html

    @api.model
    def get_average_rating(self):
        """
        Calcular la calificación promedio de todas las reseñas aprobadas
        """
        approved_reviews = self.search([('state', '=', 'approved')])
        if not approved_reviews:
            return 0

        total_rating = sum(int(review.rating) for review in approved_reviews)
        average = total_rating / len(approved_reviews)
        return round(average, 1)
