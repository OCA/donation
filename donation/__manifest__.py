# Copyright 2014-2016 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2016 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation',
    'version': '12.0.1.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage donations',
    'author': 'Barroux Abbey, Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/donation',
    'depends': [
        'donation_base'
    ],
    'data': [
        'security/donation_security.xml',
        'security/ir.model.access.csv',
        'wizard/tax_receipt_option_switch_view.xml',
        'views/donation.xml',
        'views/account.xml',
        'views/donation_campaign.xml',
        'views/users.xml',
        'views/partner.xml',
        'report/donation_report_view.xml',
        'wizard/donation_validate_view.xml',
        ],
    'post_init_hook': 'update_account_journal',
    'demo': [
        'demo/donation_demo.xml'
    ],
    'installable': True,
}
