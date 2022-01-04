import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-donation',
        'odoo14-addon-donation_base',
        'odoo14-addon-donation_direct_debit',
        'odoo14-addon-donation_recurring',
        'odoo14-addon-donation_sale',
        'odoo14-addon-product_analytic_donation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
