{
    "name": "Website Checkout Simple",
    "version": "18.0.3.0.0",
    "license": "LGPL-3",
    "category": "Website",
    "summary": (
        "Checkout reducido solo para el visitante sin cuenta: pantalla de contacto "
        "(/shop/contact) con nombre y teléfono obligatorios y email configurable, "
        "dirección en el paso de entrega, empresa/AFIP/país ocultos y valores por "
        "defecto del sistema"
    ),
    "depends": ["website_sale", "l10n_ar_website_sale"],
    "data": [
        "views/address_templates.xml",
    ],
    "installable": True,
}
