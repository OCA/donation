import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-donation',
        'odoo10-addon-donation_bank_statement',
        'odoo10-addon-donation_base',
        'odoo10-addon-donation_direct_debit',
        'odoo10-addon-donation_recurring',
        'odoo10-addon-donation_sale',
        'odoo10-addon-donation_thanks',
        'odoo10-addon-product_analytic_donation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
