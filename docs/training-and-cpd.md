# Training and CPD

**Module:** Non Profit · **Sidebar:** Non Profit → *Training & CPD*, *Reports → CPD Report*

Continuing Professional Development (CPD) for members. It reuses the **hrms** training doctypes (Training Program, Training Event, Training Result, Training Feedback) with members in place of employees, and adds a Training Session doctype of its own.

hrms must be installed. The patches below add custom fields to hrms doctypes, and migrate fails without them.

## Fields added to hrms doctypes

| Doctype | Field | Type | Notes |
| --- | --- | --- | --- |
| Training Program | cpd_hour | Data | CPD hours the programme is worth. |
| Training Event | cpd_hour | Data, read only | Fetched from the Training Program. |
| Training Event Employee | member, member_name | Link → Member, Data | Lets an event list members as attendees. |
| Training Result Employee | member, member_name | Link → Member, Data | |
| Training Feedback | member, member_name | Link → Member, Data | |

A property setter makes **Training Feedback → Employee** optional, so feedback can be recorded for a member who is not an employee.

## Hooks on hrms doctypes

These run as `doc_events` alongside hrms's own controllers.

| Doctype | Event | What it does |
| --- | --- | --- |
| Training Result | validate | Requires the Training Event to be submitted. |
| Training Result | on_submit | Marks the event *Completed*, and each attendee row whose `member` matches a result row *Completed*. |
| Training Feedback | validate | Requires the event to be submitted, the member to be listed on it, and their attendance not to be *Absent*. |
| Training Feedback | on_submit | Sets the member's attendee row to *Feedback Submitted*. |
| Training Feedback | on_cancel | Sets it back to *Completed*. |

On the Training Result form, choosing a Training Event fills the result table with the event's attendees by member.

## Training Session

A non_profit doctype, named by its **Event Name**, submittable, System Manager only.

| Field | Type | Notes |
| --- | --- | --- |
| event_name | Data, required | Also the document name. |
| training_program | Link → Training Program | |
| event_status | Select: Scheduled / Completed / Cancelled, required | Editable after submit. |
| type | Select: Seminar / Theory / Workshop / Conference / Exam / Internet / Self-study, required | |
| level | Select: Beginner / Intermediate / Advance | |
| location | Data, required | |
| start_time, end_time | Datetime | End must be after start. |
| members | Table → Training Session Member | member, status, attendance, is_mandatory |

When *Event Status* is changed after submit:
- **Completed:** every member marked *Present* whose status isn't *Feedback Submitted* becomes *Completed*.
- **Scheduled:** every member goes back to *Open*.

The **Training Result** and **Training Feedback** buttons open those lists filtered on `training_event` = this session's name. Those doctypes link to *Training Event*, not Training Session, so the filter only finds records when an event has the same name.

## CPD Report

Script report on Training Event, System Manager only. It lists one row per attendee per event.

| Filter | Notes |
| --- | --- |
| Start Date (required) | Events whose start time is on or after this date. |
| End Date (required) | Events whose end time is on or before this date. End time is a datetime, so an event ending at 17:00 on the End Date is **excluded**. Pick the next day to include it. |
| Training Program | |
| Member | |

Columns: Member ID, Member Name, Start Date, End Date, Program, CPD Hour, Type, Location.

The report doesn't filter on docstatus, so draft and cancelled Training Events are included. Events with no attendees appear once with an empty member.
