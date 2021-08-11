To configure this module, you need to:

 * create donation products
 * make sure you have an inbound payment mode for each payment mode used to receive donations. This payment mode must be configured with *Link to Bank Account* set to *Fixed* and with the donation option active.
 * if you wish to have a control amount on the donation, add the users to the group *Donation Check Total*

If you receive donations via credit transfer, you must also:

* in the configuration page *Invoicing > Configuration > Settings*, in the *Donations* section, select the product that will be used for donations by credit transfer.
* on the bank journals corresponding to the bank accounts on which you receive donations by credit transfer, in the *Payments Configuration* tab, select the *Donation by credit transfer account*. This account must allow reconciliation.
* Make sure that the accountant that processes bank statements has *User* access level or higher on the *Donation* application.
