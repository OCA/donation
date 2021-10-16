import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-donation',
        'odoo9-addon-donation_bank_statement',
        'odoo9-addon-donation_base',
        'odoo9-addon-donation_direct_debit',
        'odoo9-addon-donation_recurring',
        'odoo9-addon-donation_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
