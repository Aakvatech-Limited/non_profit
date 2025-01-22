// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Result", {
	training_event: function (frm) {
        console.log("jisdfhiaudfh");
        
		if (frm.doc.training_event) {
			frappe.call({
				method: "non_profit.non_profit.custom_doctype.training_results.get_employees",
				args: {
					training_event: frm.doc.training_event,
				},
				callback: function (r) {
                    console.log(r.message);
					frm.clear_table("employees");
					if (r.message) {
                        console.log(r.message);
						$.each(r.message, function (i, d) {
							var row = frappe.model.add_child(
								frm.doc,
								"Training Result Employee",
								"employees",
							);
							row.member = d.member;
							row.member_name = d.member_name;
						});
					}
					refresh_field("employees");
				},
			});
		}
	},
});
