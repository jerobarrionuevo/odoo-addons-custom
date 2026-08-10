from odoo import models


class Website(models.Model):
    _inherit = 'website'

    def _display_partner_b2b_fields(self):
        # This store never invoices as a business: company name, VAT/CUIT
        # number, and the AFIP responsibility/identification fields injected
        # by l10n_ar_website_sale all render inside this same condition, so
        # forcing it off hides all four without touching any template.
        return False
