.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Donation Direct Debit
=====================

With this module, when you validate a donation that has a payment method linked to a SEPA direct debit payment mode :

* if a draft direct debit order for SEPA Direct Debit already exists, a new payment line is added to it for that donation,

* otherwise, a new SEPA direct debit order is created for this donation.

Configuration
=============

In the menu *Accounting > Configuration > Miscellaneous > Payment Mode*, make sure that you have a payment mode for SEPA Direct Debit that is linked to an Account Journal allowed for donations.

Usage
=====

Validate the donations as usual !

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/180/9.0

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
