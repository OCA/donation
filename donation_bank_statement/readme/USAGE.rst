To use the module, you should import your bank statement as usual.
During the reconciliation step, when you have a donation by credit
transfer, you should set the account that you used as default
debit/credit account on the journal dedicated for donations via credit
transfer. When you validate the bank statement, Odoo will create draft
donations linked to the related bank statement line. When these draft
donations are validated, it will create the corresponding account move
and reconcile it with the account move of the bank statement.

Hint: for a faster processing of the bank statement, you can create a *Reconciliation Model* dedicated to the Donations via Credit Transfer in the menu *Accounting > Dashboard > Bank Journal > More > Reconciliation Models*. This reconciliation model must be configured with the account corresponding to the donations via credit transfer.
