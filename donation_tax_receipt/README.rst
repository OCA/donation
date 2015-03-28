Donation
========

This module handles tax receipt for donations. It is used in France by the Barroux Abbey, but it doesn't have any France-specific behavior.

Installation
============

This module depend on the module *account_auto_fy_sequence* which can be found in the OCA project *account-financial-tools* https://github.com/OCA/account-financial-tools/.

Configuration
=============

To configure this module, you need to:

 * on the donation products, you may activate the option *Is Eligible for a Tax Receipt*
 * on each donor (i.e. partner), select the *Tax Receipt Option* : *None*, *For Each Donation* or *Annual*.

Usage
=====

When you create a new donation, the *Tax Receipt Option* of the donor is copied on the donation.

When you validate a donation with a *Tax Receipt Option* set to *For Each Donation* that has one or several donation lines eligible for a tax receipt, it will create a new Tax Receipt linked to this donation.

At the beginning of each new year, start the wizard *Create Annual Receipts* : it will create all the annual tax receipts. An annual tax receipt is linked to one or several donations.

Credits
=======

Contributors
------------

* Brother Bernard <informatique - at - barroux.org>
* Brother Irénée (Barroux Abbey)
* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
