import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-donation>=16.0dev,<16.1dev',
        'odoo-addon-donation_bank_statement_oca>=16.0dev,<16.1dev',
        'odoo-addon-donation_base>=16.0dev,<16.1dev',
        'odoo-addon-donation_recurring>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
