To configure this module, you need to:

 * create donation products
 * set the *Tax Receipt Option* on partners

By default, there will be a tax receipt for each donation.
If you want "Annual Tax Receipts" for everyone, do this:

* Open a contact with no parent. Under Sale & Purchase, Fiscal Information,
  set the Tax Receipt Option to Annual Tax Receipt and save.
* Activate the Developer mode (debug=1). In the developer tools menu (bug icon),
  Set Defaults. Select "Tax Receipt Option = Annual Tax Receipt" for "All users"
  and "Save default."
* Update all existing contacts.
* * In list view, select ALL contacts, click Action - Export.
* * Select "I want to update data (import-compatible export)".
* * Add the "Tax Receipt Option" to the list of fields to export.
* * Export, download, open the spreadsheet, set "Annual Tax Receipt" on all lines, save.
* * Odoo contact list - Favorites - Import records - Load file - Import.
