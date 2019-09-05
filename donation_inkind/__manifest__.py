{
    'name': 'Donation in kind',
    'version': '11.0.1.0.0',
    'summary': 'Module to manage physical inkind donations',
    'category': 'Some Category',
    'license': 'AGPL-3',
    'author': 'Benjamin Brich, Thore Baden, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/donation',
    'contributors': [
        'Benjamin Brich',
        'Thore Baden'
    ],
    'depends': [
        'donation',
        'stock',
    ],
    'data': [
        'views/donation_donation.xml',
    ],
    'demo': [
        'demo/donation_inkind_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
