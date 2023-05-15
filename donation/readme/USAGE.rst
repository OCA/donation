This module handles donations by cash, check or by credit transfer:

* for donation by cash or check, you should first create a new donation and validate it. Then, if you have the module *account_check_deposit* from the project `OCA/account-financial-tools <https://github.com/OCA/account-financial-tools>`_, you can create a check deposit.
* for a donation by credit transfer, the process is different: import your bank statement file and, while processing it, you will see a donation button that allow you to create a new donation directly from the bank statement reconcile interface.

When you validate a donation:

* it will create a journal entry that goes directly from the revenue account to the payment account without going through a receivable account.
* if the tax receipt option of the donor is configured as *For Each Donation* and the product of the donation line is eligible to a tax receipt, it will generate the tax receipt.

To have some statistics about the donations, go to the menu Donation > Reporting > Donations Analysis.
