{
    "name": "Website Checkout Simple",
    "version": "18.0.2.0.0",
    "license": "LGPL-3",
    "category": "Website",
    "summary": (
        "Reduce el formulario de dirección del checkout a nombre, teléfono y "
        "email; oculta empresa/AFIP/país y colapsa la dirección opcional"
    ),
    "depends": ["website_sale", "l10n_ar_website_sale"],
    "data": [
        "views/address_templates.xml",
    ],
    "installable": True,
}
