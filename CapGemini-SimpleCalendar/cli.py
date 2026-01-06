"""
Command Line Interface Module

This module contains all the functions for user interaction.
It handles displaying menus, getting user input, and formatting output.
"""

from datetime import datetime

from calendar_manager import Calendar


# =============================================================================
# HELPER FUNCTIONS FOR DISPLAY
# =============================================================================

def print_header(title):
    """
    Print a formatted header for menu sections.
    
    Args:
        title (str): The header text to display
    """
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_events(events, empty_message="No events found."):
    """
    Display a list of events in a formatted way.
    
    Args:
        events (list): List of Event objects to display
        empty_message (str): Message to show if the list is empty
    """
    if not events:
        print(f"  {empty_message}")
        return
    
    for i, event in enumerate(events, 1):
        time_range = f"{event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}"
        print(f"  {i}. {event.title}")
        print(f"     Time: {time_range}")
        print()


# =============================================================================
# INPUT HELPER FUNCTIONS
# =============================================================================

def get_date_input(prompt, allow_empty=False):
    """
    Get a valid date from the user.
    
    Args:
        prompt (str): The prompt to show the user
        allow_empty (bool): If True, empty input returns today's date
        
    Returns:
        date: The parsed date, or None if cancelled
    """
    while True:
        user_input = input(prompt).strip()
        
        # Allow empty input to mean "today" if specified
        if not user_input and allow_empty:
            return datetime.now().date()
        
        if not user_input:
            print("  Please enter a date or type 'cancel' to go back.")
            continue
        
        if user_input.lower() == "cancel":
            return None
        
        # Try to parse the date in common formats (MM-DD-YYYY is preferred)
        date_formats = ["%m-%d-%Y", "%m/%d/%Y", "%Y-%m-%d"]
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(user_input, date_format).date()
                
                # Prevent scheduling events in the past - users shouldn't be able to
                # create appointments for dates that have already occurred
                if parsed_date < datetime.now().date():
                    print("  Cannot schedule events in the past. Please enter today's date or a future date.")
                    break
                
                return parsed_date
            except ValueError:
                continue
        else:
            # This else belongs to the for loop - it only runs if no format matched
            # (i.e., the loop completed without breaking due to a past date rejection)
            print("  Invalid date format. Please use MM-DD-YYYY or MM/DD/YYYY")


def get_time_input(prompt, date):
    """
    Get a valid time from the user and combine it with a date.
    
    Args:
        prompt (str): The prompt to show the user
        date (date): The date to combine with the time
        
    Returns:
        datetime: The combined date and time, or None if cancelled
    """
    while True:
        user_input = input(prompt).strip()
        
        if user_input.lower() == "cancel":
            return None
        
        if not user_input:
            print("  Please enter a time or type 'cancel' to go back.")
            continue
        
        # Try various time formats
        time_formats = [
            "%I:%M %p",  # 2:30 PM
            "%I:%M%p",   # 2:30PM
            "%H:%M",     # 14:30 (24-hour)
            "%I %p",     # 2 PM
            "%I%p",      # 2PM
        ]
        
        for time_format in time_formats:
            try:
                parsed_time = datetime.strptime(user_input.upper(), time_format).time()
                return datetime.combine(date, parsed_time)
            except ValueError:
                continue
        
        print("  Invalid time format. Examples: 2:30 PM, 14:30, 9 AM")


# ********************
# MENU FLOW FUNCTIONS
# ********************

def create_event_flow(calendar):
    """
    Guide the user through creating a new event.
    
    Args:
        calendar (Calendar): The calendar to add the event to
    """
    print_header("Create New Event")
    
    # Get the event title
    title = input("  Enter event title (or 'cancel'): ").strip()
    if not title or title.lower() == "cancel":
        print("  Event creation cancelled.")
        return
    
    # Get the date for the event
    print("\n  Enter the date for this event:")
    event_date = get_date_input("  Date (MM-DD-YYYY) or press Enter for today: ", allow_empty=True)
    if event_date is None:
        print("  Event creation cancelled.")
        return
    
    # Get the start time
    print(f"\n  Date selected: {event_date.strftime('%A, %B %d, %Y')}")
    
    while True:
        start_time = get_time_input("  Start time (e.g., 9:00 AM): ", event_date)
        if start_time is None:
            print("  Event creation cancelled.")
            return
        
        # If the user selected today's date, make sure the start time hasn't already passed
        # since it doesn't make sense to schedule an event that's already in the past
        if event_date == datetime.now().date() and start_time < datetime.now():
            print("  Cannot schedule events in the past. Please enter a future time.")
            continue
        
        break
    
    # Get the end time
    end_time = get_time_input("  End time (e.g., 10:00 AM): ", event_date)
    if end_time is None:
        print("  Event creation cancelled.")
        return
    
    # Try to add the event
    success, message = calendar.add_event(title, start_time, end_time)
    print(f"\n  {message}")


def view_events_flow(calendar):
    """
    Show events for a specific date.
    
    Args:
        calendar (Calendar): The calendar to read from
    """
    print_header("View Events for a Date")
    
    target_date = get_date_input("  Enter date (MM-DD-YYYY) or press Enter for today: ", allow_empty=True)
    if target_date is None:
        return
    
    print(f"\n  Events for {target_date.strftime('%A, %B %d, %Y')}:\n")
    events = calendar.get_events_for_date(target_date)
    print_events(events, "No events scheduled for this date.")


def view_remaining_events_flow(calendar):
    """
    Show remaining events for today.
    
    Args:
        calendar (Calendar): The calendar to read from
    """
    print_header("Remaining Events Today")
    
    today = datetime.now().date()
    print(f"  Date: {today.strftime('%A, %B %d, %Y')}")
    print(f"  Current time: {datetime.now().strftime('%I:%M %p')}\n")
    
    events = calendar.get_remaining_events_today()
    print_events(events, "No remaining events for today.")


def find_slot_flow(calendar):
    """
    Find an available time slot for a meeting.
    
    Args:
        calendar (Calendar): The calendar to search in
    """
    print_header("Find Available Time Slot")
    
    # Get the duration needed
    while True:
        duration_input = input("  How many minutes do you need? (e.g., 30, 60): ").strip()
        
        if duration_input.lower() == "cancel":
            return
        
        try:
            duration = int(duration_input)
            if duration <= 0:
                print("  Please enter a positive number.")
                continue
            break
        except ValueError:
            print("  Please enter a valid number.")
    
    # Get the date to search
    target_date = get_date_input("  Enter date (MM-DD-YYYY) or press Enter for today: ", allow_empty=True)
    if target_date is None:
        return
    
    # Search for an available slot
    slot = calendar.find_next_available_slot(duration, target_date)
    
    print(f"\n  Searching for a {duration}-minute slot on {target_date.strftime('%A, %B %d, %Y')}...")
    
    if slot:
        start, end = slot
        print(f"\n  Available slot found!")
        print(f"  Time: {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
    else:
        print("\n  No available slot found for the requested duration.")
        print("  Try a shorter duration or a different date.")


def delete_event_flow(calendar):
    """
    Delete an event from the calendar.
    
    Args:
        calendar (Calendar): The calendar to delete from
    """
    print_header("Delete an Event")
    
    # Get the date
    target_date = get_date_input("  Enter date of event (MM-DD-YYYY) or press Enter for today: ", allow_empty=True)
    if target_date is None:
        return
    
    # Show events for that date
    events = calendar.get_events_for_date(target_date)
    
    if not events:
        print(f"\n  No events found for {target_date.strftime('%A, %B %d, %Y')}.")
        return
    
    print(f"\n  Events for {target_date.strftime('%A, %B %d, %Y')}:\n")
    print_events(events)
    
    # Ask which event to delete
    while True:
        choice = input(f"  Enter event number to delete (1-{len(events)}) or 'cancel': ").strip()
        
        if choice.lower() == "cancel":
            print("  Deletion cancelled.")
            return
        
        try:
            event_num = int(choice)
            success, message = calendar.delete_event(event_num, target_date)
            print(f"\n  {message}")
            return
        except ValueError:
            print("  Please enter a valid number.")


def show_main_menu():
    """
    Display the main menu options.
    """
    print("\n" + "-" * 50)
    print("  MAIN MENU")
    print("-" * 50)
    print("  1. Create a new event")
    print("  2. View all events for a date")
    print("  3. View remaining events for today")
    print("  4. Find next available time slot")
    print("  5. Delete an event")
    print("  6. Exit")
    print("-" * 50)


def run_cli():
    """
    Main application entry point.
    
    Displays the menu and handles user interaction in a loop.
    """
    print("\n" + "=" * 50)
    print("  SIMPLE CALENDAR & APPOINTMENT MANAGER")
    print("=" * 50)
    
    # Initialize the calendar (this will load any saved events)
    calendar = Calendar()
    
    # Main application loop
    while True:
        # Display the main menu
        show_main_menu()
        
        choice = input("  Enter your choice (1-6): ").strip()
        
        if choice == "1":
            create_event_flow(calendar)
        elif choice == "2":
            view_events_flow(calendar)
        elif choice == "3":
            view_remaining_events_flow(calendar)
        elif choice == "4":
            find_slot_flow(calendar)
        elif choice == "5":
            delete_event_flow(calendar)
        elif choice == "6":
            print("\n  Thank you for using Simple Calendar!")
            print("  Your events have been saved. Goodbye!\n")
            break
        else:
            print("\n  Invalid choice. Please enter a number between 1 and 6.")

