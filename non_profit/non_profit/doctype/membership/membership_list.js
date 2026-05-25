frappe.listview_settings['Membership'] = {
	get_indicator: function(doc) {
		if (doc.membership_status == 'New') {
			return [__('New'), 'blue', 'membership_status,=,New'];
		} else if (doc.membership_status === 'Current') {
			return [__('Current'), 'green', 'membership_status,=,Current'];
		} else if (doc.membership_status === 'Pending') {
			return [__('Pending'), 'yellow', 'membership_status,=,Pending'];
		} else if (doc.membership_status === 'Expired') {
			return [__('Expired'), 'grey', 'membership_status,=,Expired'];
		} else {
			return [__('Cancelled'), 'red', 'membership_status,=,Cancelled'];
		}
	},
    onload: function (listview) {
        listview.page.add_menu_item(__('Bulk Sales Orders'), async function () {
            const selected_docs = listview.get_checked_items();
            if (selected_docs.length === 0) {
                frappe.msgprint(__('Please select at least one document.'));
                return;
            }
			frappe.call({
				method: 'non_profit.non_profit.doctype.membership.membership.generate_bulk_sales_order',
				args: {
					doc: selected_docs
				},
				freeze: true,
				freeze_message: __("Creating Bulk Membership Sales Orders"),
				callback: function(r) {
					if (r.message)
						frappe.msgprint(_("Sales Order(s) created successfully"))
				}
			   });
			console.log(selected_docs);
			
        });
    }
};
