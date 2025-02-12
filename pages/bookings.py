import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(page_title="Customized Calendar Demo", page_icon="📅")

# New font and color scheme
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f7fc;
        }
        .fc-event {
            border-radius: 8px;
            font-weight: bold;
        }
        .fc-toolbar-title {
            font-size: 2.5rem;
            color: #4a90e2;
        }
        .fc-event-title {
            color: #ffffff;
            font-size: 1rem;
        }
        .fc-event-past {
            opacity: 0.7;
        }
        .fc-daygrid-day-number {
            color: #e14e52;
        }
        .fc-event-time {
            font-style: italic;
        }
    </style>
""", unsafe_allow_html=True)

# Custom calendar mode selector
calendar_modes = [
    "Day Grid", "Time Grid", "Timeline", 
    "Resource Day Grid", "Resource Time Grid", "Resource Timeline", 
    "List View", "Multi Month View"
]

mode = st.selectbox("Select Calendar Mode:", calendar_modes)

# Custom events with different start/end times and colors
events = [
    {"title": "Team Meeting", "color": "#F26D21", "start": "2023-09-12", "end": "2023-09-13", "resourceId": "room1"},
    {"title": "Project Deadline", "color": "#22B8FF", "start": "2023-09-05", "end": "2023-09-05", "resourceId": "room2"},
    {"title": "Client Call", "color": "#8E44AD", "start": "2023-09-20T09:30:00", "end": "2023-09-20T11:00:00", "resourceId": "room3"},
    {"title": "Team Lunch", "color": "#FFB142", "start": "2023-09-15T12:00:00", "end": "2023-09-15T13:00:00", "resourceId": "room4"},
    {"title": "Workshop", "color": "#30D158", "start": "2023-09-22T14:00:00", "end": "2023-09-22T16:00:00", "resourceId": "room5"},
]

calendar_resources = [
    {"id": "room1", "building": "Main Office", "title": "Conference Room 1"},
    {"id": "room2", "building": "Main Office", "title": "Conference Room 2"},
    {"id": "room3", "building": "Annex", "title": "Meeting Room A"},
    {"id": "room4", "building": "Main Office", "title": "Cafeteria"},
    {"id": "room5", "building": "Annex", "title": "Training Room"},
]

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "resources": calendar_resources,
    "selectable": "true",
}

# Adjust options based on the selected mode
if "resource" in mode.lower():
    if "resource day grid" in mode.lower():
        calendar_options.update({
            "initialDate": "2023-09-01",
            "initialView": "resourceDayGridDay",
            "resourceGroupField": "building",
        })
    elif "resource timeline" in mode.lower():
        calendar_options.update({
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth"},
            "initialDate": "2023-09-01",
            "initialView": "resourceTimelineDay",
            "resourceGroupField": "building",
        })
    elif "resource time grid" in mode.lower():
        calendar_options.update({
            "initialDate": "2023-09-01",
            "initialView": "resourceTimeGridDay",
            "resourceGroupField": "building",
        })
else:
    if "day grid" in mode.lower():
        calendar_options.update({
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridDay,dayGridWeek,dayGridMonth"},
            "initialDate": "2023-09-01",
            "initialView": "dayGridMonth",
        })
    elif "time grid" in mode.lower():
        calendar_options.update({
            "initialView": "timeGridWeek",
        })
    elif "timeline" in mode.lower():
        calendar_options.update({
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": "timelineDay,timelineWeek,timelineMonth"},
            "initialDate": "2023-09-01",
            "initialView": "timelineMonth",
        })
    elif "list" in mode.lower():
        calendar_options.update({
            "initialDate": "2023-09-01",
            "initialView": "listMonth",
        })
    elif "multi month" in mode.lower():
        calendar_options.update({
            "initialView": "multiMonthYear",
        })

# Display the calendar with customized styles
state = calendar(
    events=st.session_state.get("events", events),
    options=calendar_options,
    custom_css="""
    .fc-event-past {
        opacity: 0.7;
    }
    .fc-event-title {
        font-size: 1rem;
    }
    .fc-toolbar-title {
        font-size: 2.5rem;
        color: #4a90e2;
    }
    """,
    key=mode,
)

# Store the new events if they are modified
if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]

st.write(state)
