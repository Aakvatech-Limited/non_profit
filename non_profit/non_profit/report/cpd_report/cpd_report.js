// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["CPD Report"] = {
    filters: [
        {
            fieldname: "start_date",
            label: __("Start Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start(), // Default to the start of the current month
            description: __("Filter sessions starting from this date"),
        },
        {
            fieldname: "end_date",
            label: __("End Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end(), // Default to the end of the current month
            description: __("Filter sessions ending on this date"),
        },
        {
            fieldname: "training_program",
            label: __("Training Program"),
            fieldtype: "Link",
            options: "Training Program", // Assuming "Training Program" is a DocType
            description: __("Filter by specific training program"),
        },
        {
            fieldname: "member",
            label: __("Member ID"),
            fieldtype: "Link",
            options: "Member", // Assuming "Member" is a DocType
            description: __("Filter by Member ID"),
        }
    ],
};
