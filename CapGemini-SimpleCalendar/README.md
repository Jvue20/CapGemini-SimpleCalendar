# Simple Calendar & Appointment Manager

A command-line Python application for managing calendar events and appointments. This application allows you to create, view, and manage events while preventing scheduling conflicts.

## Features

- **Create Events**: Add new events with a title, start time, and end time
- **Overlap Prevention**: The system automatically prevents scheduling conflicting events
- **View Events by Date**: See all events for any specified day
- **View Remaining Events**: See events that haven't ended yet for today
- **Find Available Slots**: Quickly find the next open time slot of a specified duration
- **Delete Events**: Remove events you no longer need
- **Data Persistence**: Events are saved to a JSON file and persist between sessions

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/SimpleCalendar.git
   cd SimpleCalendar
   ```

2. No additional installation needed - the application uses only Python's standard library.

## Usage

Run the application:

```bash
python main.py
```

### Main Menu Options

```
1. Create a new event
2. View all events for a date
3. View remaining events for today
4. Find next available time slot
5. Delete an event
6. Exit
```

### Creating an Event

1. Select option `1` from the main menu
2. Enter the event title
3. Enter the date (MM-DD-YYYY format, or press Enter for today)
4. Enter the start time (e.g., "9:00 AM" or "14:30")
5. Enter the end time (e.g., "10:00 AM" or "15:00")

The system will check for conflicts and notify you if the time slot is already taken.

### Viewing Events

- **Option 2**: View all events for any date you specify
- **Option 3**: View only the remaining events for today (events that haven't ended yet)

### Finding Available Time Slots

1. Select option `4` from the main menu
2. Enter the duration you need (in minutes)
3. Enter the date to search (or press Enter for today)
4. The system will find the next available slot within business hours (8 AM - 6 PM)

### Time Format Examples

The application accepts multiple time formats:
- `9:00 AM` or `9:00 am`
- `2:30 PM` or `2:30PM`
- `14:30` (24-hour format)
- `9 AM` or `2 PM`

### Date Format Examples

The application accepts multiple date formats:
- `01-15-2026` (MM-DD-YYYY) - preferred format
- `01/15/2026` (MM/DD/YYYY)
- `2026-01-15` (YYYY-MM-DD)

## Running Tests

The project includes unit tests to verify the core functionality works correctly.

Run all tests:
```bash
python -m unittest test_calendar.py -v
```

The `-v` flag shows verbose output with each test name and result.

### What the Tests Cover

- **Overlap Detection**: Various scenarios for events that should and shouldn't overlap
- **Event Serialization**: Converting events to/from JSON format
- **Adding Events**: Valid events, invalid times, and overlap prevention
- **Retrieving Events**: Getting events by date, sorted order
- **Finding Available Slots**: Empty calendar, gaps between events, fully booked days
- **Deleting Events**: Valid and invalid deletion attempts
- **Data Persistence**: Events survive app restart

## Data Storage

Events are stored in `calendar_data.json` in the same directory as the application. This file is created automatically when you add your first event.

Example of stored data:
```json
[
  {
    "title": "Team Meeting",
    "start_time": "2026-01-15T09:00:00",
    "end_time": "2026-01-15T10:00:00"
  }
]
```

## Project Structure

The application is organized into multiple files for clarity:

```
SimpleCalendar/
├── main.py              # Entry point - run this to start the app
├── event.py             # Event class definition
├── calendar_manager.py  # Calendar class with all event management logic
├── cli.py               # Command-line interface and user interaction
├── test_calendar.py     # Unit tests
├── calendar_data.json   # Data storage (created automatically)
└── README.md            # This file
```

### event.py - Event Class
Represents a single calendar event with:
- Title, start time, and end time
- Methods to check for overlaps with other events
- Serialization to/from JSON for storage

### calendar_manager.py - Calendar Class
Manages the collection of events with methods to:
- Add events (with overlap checking)
- Get events for a specific date
- Get remaining events for today
- Find available time slots
- Delete events
- Save/load from JSON file

### cli.py - Command Line Interface
Handles all user interaction:
- Menu display and navigation
- Input validation for dates and times
- Formatted output for events

## Example Session

```
==================================================
  SIMPLE CALENDAR & APPOINTMENT MANAGER
==================================================
No existing calendar data found. Starting with empty calendar.

--------------------------------------------------
  MAIN MENU
--------------------------------------------------
  1. Create a new event
  2. View all events for a date
  3. View remaining events for today
  4. Find next available time slot
  5. Delete an event
  6. Exit
--------------------------------------------------
  Enter your choice (1-6): 1

==================================================
  Create New Event
==================================================
  Enter event title (or 'cancel'): Team Standup

  Enter the date for this event:
  Date (MM-DD-YYYY) or press Enter for today: 

  Date selected: Tuesday, January 06, 2026
  Start time (e.g., 9:00 AM): 9:00 AM
  End time (e.g., 10:00 AM): 9:30 AM

  Event 'Team Standup' added successfully!
```

## Design Decisions

1. **In-Memory + File Storage**: Events are kept in memory for fast access and persisted to JSON for durability between sessions.

2. **Simple Overlap Detection**: Two events overlap if one starts before the other ends AND ends after the other starts. This handles all edge cases cleanly.

3. **Business Hours for Slot Finding**: Available slot search is limited to 8 AM - 6 PM by default. This can be easily modified in the code.

4. **Flexible Input Parsing**: The application accepts multiple date and time formats for user convenience.




