// Copyright (c) 2024, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Member Employer', {
    refresh(frm) {
        // Check if the document is saved (not new)
        if (!frm.is_new()) {
            frm.add_custom_button(__('Bulk Membership Sales Order'), function() {
				frm.call({
					doc: frm.doc,
					method: "generate_bulk_sales_order",
					args: {save: true},
					freeze: true,
					freeze_message: __("Creating Bulk Membership Sales Order"),
					callback: function(r) {
						if (r.message)
							frm.reload_doc();
					}
				});
            });
        }
		if (frm.doc.invoice) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Sales Invoice',
					filters: { name: frm.doc.invoice, status: 'Paid' },
					fieldname: ['status']
				},
				callback: function(r) {
					if (r.message && r.message.status) {
						const status = r.message.status;
						if (status === 'Paid') {
							frm.set_value('paid', 1);
							frm.save();
						}
					}
				}
			});
		}
		
    }
});
