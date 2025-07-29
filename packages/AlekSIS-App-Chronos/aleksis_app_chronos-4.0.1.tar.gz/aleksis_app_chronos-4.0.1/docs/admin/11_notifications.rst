Setup notifications about current changes
=========================================

Users can get notifications about current changes to their personal timetables.
To activate this behavior, the system administrator has to ensure multiple things:

* The notifications have been activated in the preferences (see below).
* There is at least one notification channel available to your users (cf. :ref:`core-admin-notifications`).

Preferences
-----------

You can customize the way how and when notifications are sent at the configuration page at *Admin → Configuration → Timetables*:

* **Send notifications to affected teachers when substitution lessons are created or edited:**
  With this checkbox, the whole feature can be activated or deactivated.
* **Trigger mode for lesson event alarms:** Notifications can be sent at a fixed time one or more days earlier or relative to the events start time.
* **How many days in advance should lesson event alarms be sent?** Here the number of days can be configured notifications will be sent
  before the actual affected day. A common value is one or two days.
* **Time for sending lesson event alarms:** At this time, the notifications for the next days will be sent (if fixed select, see above).
  This is only used if the changes are created before the period configured with the above mentioned option. If they affect a day in this period,
  the notification will be sent immediately.
* **How much in advance should lesson event alarms be sent?**: This says how early notifications should be sent (in relation to the lesson start time).
