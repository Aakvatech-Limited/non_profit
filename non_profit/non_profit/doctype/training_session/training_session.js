// Copyright (c) 2024, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Session', {
	onload_post_render: function (frm) {
		frm.get_field("members").grid.set_multiple_add("member");
	},
	refresh: function (frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__("Training Result"), function () {
				frappe.route_options = {
					training_event: frm.doc.name,
				};
				frappe.set_route("List", "Training Result");
			});
			frm.add_custom_button(__("Training Feedback"), function () {
				frappe.route_options = {
					training_event: frm.doc.name,
				};
				frappe.set_route("List", "Training Feedback");
			});
		}
		frm.events.set_member_query(frm);
	},

	set_member_query: function (frm) {
		let emp = [];
		for (let d in frm.doc.members) {
			if (frm.doc.members[d].member) {
				emp.push(frm.doc.members[d].member);
			}
		}
		frm.set_query("member", "members", function () {
			return {
				filters: {
					name: ["NOT IN", emp],
				},
			};
		});
	},
});
frappe.ui.form.on("Training Session Member", {
	member: function (frm) {
		frm.events.set_employee_query(frm);
	},
});