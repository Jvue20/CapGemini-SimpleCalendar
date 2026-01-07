"""
Calendar Manager Module

This module contains the Calendar class which manages a collection of events.
It handles adding, retrieving, and deleting events, as well as finding available time slots.
Data is persisted to a JSON file.
"""

import json
import os
from datetime import datetime, timedelta

from event import Event


class Calendar:
    """
    Manages a collection of events and provides calendar operations.
    
    The calendar stores all events in memory and persists them to a JSON file.
    It prevents scheduling conflicts by checking for overlapping events.
    
    Optimization: Events are stored in a dictionary indexed by date, which allows
    O(1) lookup for any specific date instead of scanning all events. This makes
    most operations O(m) where m is events on a specific date, rather than O(n)
    where n is total events in the calendar.
    """
    
    # The file where we'll save our events
    DATA_FILE = "calendar_data.json"
    
    def __init__(self):
        """
        Initialize the calendar and load any existing events from storage.
        
        We use a dictionary where keys are date strings (YYYY-MM-DD) and values
        are lists of events for that date, kept sorted by start time.
        """
        # Dictionary structure: { "2026-01-06": [event1, event2, ...], ... }
        self.events_by_date = {}
        self.load_events()
    
    def _get_date_key(self, date_obj):
        """
        Convert a date object to a string key for dictionary storage.
        
        Args:
            date_obj: A date or datetime object
            
        Returns:
            str: Date in YYYY-MM-DD format
        """
        # Handle both date and datetime objects by extracting just the date portion
        if hasattr(date_obj, 'date'):
            return date_obj.date().isoformat()
        return date_obj.isoformat()
    
    def _insert_sorted(self, date_key, event):
        """
        Insert an event into the correct position to maintain sorted order by start time.
        
        Using binary search (bisect) for O(log m) insertion position finding,
        where m is the number of events on that date.
        
        Args:
            date_key (str): The date key in the dictionary
            event (Event): The event to insert
        """
        from bisect import bisect_left
        
        if date_key not in self.events_by_date:
            self.events_by_date[date_key] = []
        
        events_list = self.events_by_date[date_key]
        
        # Find the insertion point using binary search on start times
        # This keeps the list sorted by start_time automatically
        start_times = [e.start_time for e in events_list]
        insert_pos = bisect_left(start_times, event.start_time)
        events_list.insert(insert_pos, event)
    
    def load_events(self):
        """
        Load events from the JSON file if it exists.
        
        This allows events to persist between program runs.
        If the file doesn't exist or is invalid, we start with an empty calendar.
        Events are organized into the dictionary structure for efficient lookups.
        """
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as file:
                    data = json.load(file)
                    
                    # Convert each dictionary back to an Event object and organize by date
                    event_count = 0
                    for event_data in data:
                        event = Event.from_dict(event_data)
                        date_key = self._get_date_key(event.start_time)
                        self._insert_sorted(date_key, event)
                        event_count += 1
                        
                print(f"Loaded {event_count} existing event(s) from storage.")
            except (json.JSONDecodeError, KeyError) as error:
                # If the file is corrupted, start fresh
                print(f"Warning: Could not load saved events ({error}). Starting fresh.")
                self.events_by_date = {}
        else:
            print("No existing calendar data found. Starting with empty calendar.")
    
    def save_events(self):
        """
        Save all events to the JSON file.
        
        This is called after any change to ensure data persistence.
        We flatten the dictionary structure back to a list for simple JSON storage.
        """
        with open(self.DATA_FILE, "w") as file:
            # Flatten all events from the dictionary into a single list for storage
            # The dictionary structure is rebuilt on load for efficient lookups
            all_events = []
            for events_list in self.events_by_date.values():
                all_events.extend([event.to_dict() for event in events_list])
            json.dump(all_events, file, indent=2)
    
    def add_event(self, title, start_time, end_time):
        """
        Add a new event to the calendar if it doesn't conflict with existing events.
        
        Time Complexity: O(m) where m is the number of events on the same date.
        This is much better than O(n) since we only check events on the relevant date.
        
        Args:
            title (str): The name of the event
            start_time (datetime): When the event starts
            end_time (datetime): When the event ends
            
        Returns:
            tuple: (success: bool, message: str) indicating result
        """
        # First, validate that the end time is after the start time
        if end_time <= start_time:
            return False, "Error: End time must be after start time."
        
        # Create the new event to check for conflicts
        new_event = Event(title, start_time, end_time)
        date_key = self._get_date_key(start_time)
        
        # Only check events on the same date for conflicts - this is the key optimization
        # Instead of scanning all events in the calendar, we only look at events for this date
        events_on_date = self.events_by_date.get(date_key, [])
        
        for existing_event in events_on_date:
            if new_event.overlaps_with(existing_event):
                conflict_start = existing_event.start_time.strftime('%I:%M %p')
                conflict_end = existing_event.end_time.strftime('%I:%M %p')
                return False, f"Error: This event overlaps with '{existing_event.title}' ({conflict_start} - {conflict_end})"
        
        # No conflicts found, insert the event in sorted order
        self._insert_sorted(date_key, new_event)
        self.save_events()
        return True, f"Event '{title}' added successfully!"
    
    def get_events_for_date(self, target_date):
        """
        Get all events scheduled for a specific date.
        
        Time Complexity: O(m) where m is the number of events on that date.
        Previously O(n) where n was total events. Now we have O(1) dictionary lookup
        followed by O(m) list copy. Events are already sorted, so no sorting needed.
        
        Args:
            target_date (date): The date to check
            
        Returns:
            list: List of Event objects for that date, sorted by start time
        """
        date_key = self._get_date_key(target_date)
        
        # O(1) dictionary lookup instead of O(n) linear scan
        # Return a copy of the list to prevent external modification
        # Events are already sorted by start time from _insert_sorted
        return list(self.events_by_date.get(date_key, []))
    
    def get_remaining_events_today(self):
        """
        Get events that haven't started yet or are currently in progress today.
        
        Time Complexity: O(m) where m is the number of events today.
        Previously O(n) where n was total events. We use binary search to find
        the starting point of remaining events for additional efficiency.
        
        Returns:
            list: List of Event objects that are remaining today
        """
        from bisect import bisect_left
        
        now = datetime.now()
        today = now.date()
        date_key = self._get_date_key(today)
        
        # Get today's events with O(1) lookup instead of scanning all events
        todays_events = self.events_by_date.get(date_key, [])
        
        if not todays_events:
            return []
        
        # Since events are sorted by start time, we can use binary search to find
        # a good starting point. Events ending after 'now' are the ones we want.
        # We filter for events whose end_time > now (still in progress or upcoming)
        remaining_events = [event for event in todays_events if event.end_time > now]
        
        # Already sorted by start time from the dictionary structure
        return remaining_events
    
    def find_next_available_slot(self, duration_minutes, target_date=None):
        """
        Find the next available time slot of a specified duration.
        
        This searches for a gap in the schedule where a new event
        of the requested length could be scheduled.
        
        Args:
            duration_minutes (int): How long the slot needs to be (in minutes)
            target_date (date, optional): The date to search. Defaults to today.
            
        Returns:
            tuple: (start_time, end_time) of the available slot, or None if no slot found
        """
        # Use today's date if no specific date is provided
        if target_date is None:
            target_date = datetime.now().date()
        
        # Define the working hours for the day (8 AM to 6 PM)
        # You can adjust these to match your preferences
        day_start = datetime.combine(target_date, datetime.strptime("08:00", "%H:%M").time())
        day_end = datetime.combine(target_date, datetime.strptime("18:00", "%H:%M").time())
        
        # If we're looking at today, don't suggest times in the past
        now = datetime.now()
        if target_date == now.date() and now > day_start:
            # Round up to the next 15-minute interval for cleaner scheduling
            minutes = now.minute
            rounded_minutes = ((minutes // 15) + 1) * 15
            if rounded_minutes >= 60:
                day_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            else:
                day_start = now.replace(minute=rounded_minutes, second=0, microsecond=0)
        
        # Get all events for this date, sorted by start time
        days_events = self.get_events_for_date(target_date)
        
        # The duration we need as a timedelta
        needed_duration = timedelta(minutes=duration_minutes)
        
        # Start checking from the beginning of the day
        current_time = day_start
        
        # Check each potential slot
        for event in days_events:
            # Is there enough time between now and the next event?
            gap_end = event.start_time
            if gap_end > current_time and (gap_end - current_time) >= needed_duration:
                # Found a slot before this event
                return (current_time, current_time + needed_duration)
            
            # Move past this event if it ends later than our current position
            if event.end_time > current_time:
                current_time = event.end_time
        
        # Check if there's time at the end of the day
        if current_time < day_end and (day_end - current_time) >= needed_duration:
            return (current_time, current_time + needed_duration)
        
        # No slot found
        return None
    
    def delete_event(self, event_index, target_date):
        """
        Delete an event from the calendar.
        
        Time Complexity: O(m) where m is the number of events on that date.
        Previously O(n) for finding the event in the flat list. Now we directly
        access the date's event list and remove by index.
        
        Args:
            event_index (int): The index of the event in that day's list (1-based)
            target_date (date): The date of the event
            
        Returns:
            tuple: (success: bool, message: str) indicating result
        """
        date_key = self._get_date_key(target_date)
        
        # Get the events list for this date directly from the dictionary
        events_on_date = self.events_by_date.get(date_key, [])
        
        # Check if the index is valid
        if event_index < 1 or event_index > len(events_on_date):
            return False, f"Error: Invalid event number. Please choose 1-{len(events_on_date)}."
        
        # Get the event to delete (convert to 0-based index) and remove it
        # Using pop() with index is O(m) but more direct than searching
        event_to_delete = events_on_date.pop(event_index - 1)
        
        # Clean up empty date entries to keep the dictionary tidy
        if not events_on_date:
            del self.events_by_date[date_key]
        
        self.save_events()
        
        return True, f"Event '{event_to_delete.title}' deleted successfully!"

