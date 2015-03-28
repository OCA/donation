Donation Direct Debit
=====================

With this module, when you validate a donation that has a payment method linked to a SEPA direct debit payment mode :

* if a draft direct debit order for SEPA Direct Debit already exists, a new payment line is added to it for that donation,

* otherwise, a new SEPA direct debit order is created for this donation.

Configuration
=============

In the menu Accounting > Configuration > Miscellaneous > Payment Mode, make sure that you have a payment mode for SEPA Direct Debit that is linked to an Account Journal allowed for donations.

Usage
=====

Validate the donations as usual !

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
