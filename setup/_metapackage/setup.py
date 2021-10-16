import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-donation',
        'odoo8-addon-donation_bank_statement',
        'odoo8-addon-donation_direct_debit',
        'odoo8-addon-donation_recurring',
        'odoo8-addon-donation_recurring_tax_receipt',
        'odoo8-addon-donation_tax_receipt',
        'odoo8-addon-donation_thanks',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
