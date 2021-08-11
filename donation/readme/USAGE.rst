This module handles donations by cash, check or by credit transfer:

* for donation by cash or check, you should first create a new donation and validate it. Then, if you have the module *account_check_deposit* from the project `OCA/account-financial-tools <https://github.com/OCA/account-financial-tools>`_, you can create a check deposit.
* for a donation by credit transfer, the process in inverted: first, import your bank statement file and process it. When you process a statement line that correspond to a donation by credit transfer, make sure that the partner is the good one and, in the *Manual Operations* tab, set the *Donation by credit transfer account* (configured on the corresponding bank journal) as counterpart. When you close the bank statement, Odoo will generate a draft donation for each statement line identified as a donation by credit transfer. Then you should verify and validate these draft donations.

When you validate a donation:

* it will create a journal entry that goes directly from the revenue account to the payment account without going through a receivable account.
* if the tax receipt option of the donor is configured as *For Each Donation* and the product of the donation line is eligible to a tax receipt, it will generate the tax receipt.

To have some statistics about the donations, go to the menu Donation > Reporting > Donations Analysis.
