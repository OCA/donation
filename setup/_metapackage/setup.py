import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-donation",
    description="Meta package for oca-donation Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-donation_base',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
