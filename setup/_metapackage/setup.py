import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-donation',
        'odoo11-addon-donation_bank_statement',
        'odoo11-addon-donation_base',
        'odoo11-addon-donation_direct_debit',
        'odoo11-addon-donation_recurring',
        'odoo11-addon-donation_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
