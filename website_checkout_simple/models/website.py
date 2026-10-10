from odoo import models
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def _display_partner_b2b_fields(self):
        # Empresa, CUIT/número y los campos AFIP que inyecta l10n_ar_website_sale se
        # renderizan todos dentro de esta misma condición: apagarla los oculta juntos sin
        # tocar el template. Solo para el visitante sin cuenta; el cliente logueado
        # conserva el comportamiento estándar. `request` es nulo fuera de una petición web.
        if request and self.is_public_user():
            return False
        return super()._display_partner_b2b_fields()
