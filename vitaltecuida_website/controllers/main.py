from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WebsiteReviewController(http.Controller):

    @http.route('/reviews', type='http', auth='public', website=True)
    def reviews_page(self, **kwargs):
        """
        Página principal de reseñas - muestra reseñas aprobadas y formulario
        """
        try:
            # Simplificar la lógica para evitar errores
            values = {
                'reviews': [],
                'average_rating': 0.0,
                'total_reviews': 0,
                'page_name': 'reviews',
            }

            # Intentar obtener reseñas solo si el modelo existe
            try:
                Review = request.env['website.review']
                approved_reviews = Review.search([('state', '=', 'approved')])
                values['reviews'] = approved_reviews[:20]  # Máximo 20 reseñas
                values['total_reviews'] = len(approved_reviews)

                # Calcular promedio simple
                if approved_reviews:
                    total_rating = sum(int(review.rating) for review in approved_reviews)
                    values['average_rating'] = round(total_rating / len(approved_reviews), 1)

            except Exception as model_error:
                _logger.warning(f"Error accessing review model: {str(model_error)}")
                # Continuar con valores por defecto

            return request.render('vitaltecuida_website.reviews_page', values)

        except Exception as e:
            _logger.error(f"Error rendering reviews page: {str(e)}")
            # Página de emergencia muy simple
            return request.render('website.page_404')

    @http.route('/reviews/submit', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def submit_review(self, **post):
        """
        Procesar el envío de una nueva reseña
        """
        try:
            # Validar datos requeridos
            required_fields = ['customer_name', 'rating', 'title', 'review_text']
            for field in required_fields:
                if not post.get(field):
                    return request.render('vitaltecuida_website.review_error', {
                        'error_message': f'El campo {field} es requerido.'
                    })

            # Obtener información adicional
            ip_address = request.httprequest.environ.get('REMOTE_ADDR', '')
            user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '')

            # Crear la reseña
            Review = request.env['website.review']
            review_vals = {
                'customer_name': post.get('customer_name'),
                'email': post.get('email', ''),
                'rating': post.get('rating'),
                'title': post.get('title'),
                'review_text': post.get('review_text'),
                'ip_address': ip_address,
                'user_agent': user_agent,
            }

            review = Review.sudo().create(review_vals)
            _logger.info(f"Nueva reseña recibida de {review.customer_name} (ID: {review.id})")

            # Página de confirmación
            return request.render('vitaltecuida_website.review_success', {
                'review': review,
            })

        except Exception as e:
            _logger.error(f"Error al procesar reseña: {str(e)}")
            return request.render('vitaltecuida_website.review_error', {
                'error_message': 'Ocurrió un error al procesar tu reseña. Por favor intenta nuevamente.'
            })

    @http.route('/reviews/api/list', type='json', auth='public')
    def api_get_reviews(self, limit=10):
        """
        API JSON para obtener reseñas aprobadas (para uso con JavaScript)
        """
        Review = request.env['website.review']
        reviews = Review.get_published_reviews(limit=limit)

        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'customer_name': review.customer_name,
                'rating': int(review.rating),
                'rating_stars': review.get_rating_stars_html(),
                'title': review.title,
                'review_text': review.review_text,
                'create_date': review.create_date.strftime('%d/%m/%Y') if review.create_date else '',
            })

        return {
            'reviews': reviews_data,
            'average_rating': Review.get_average_rating(),
            'total_reviews': len(Review.search([('state', '=', 'approved')])),
        }
