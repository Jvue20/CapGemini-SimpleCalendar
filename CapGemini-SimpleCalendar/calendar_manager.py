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
    """
    
    # The file where we'll save our events
    DATA_FILE = "calendar_data.json"
    
    def __init__(self):
        """
        Initialize the calendar and load any existing events from storage.
        """
        self.events = []
        self.load_events()
    
    def load_events(self):
        """
        Load events from the JSON file if it exists.
        
        This allows events to persist between program runs.
        If the file doesn't exist or is invalid, we start with an empty calendar.
        """
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as file:
                    data = json.load(file)
                    # Convert each dictionary back to an Event object
                    self.events = [Event.from_dict(event_data) for event_data in data]
                print(f"Loaded {len(self.events)} existing event(s) from storage.")
            except (json.JSONDecodeError, KeyError) as error:
                # If the file is corrupted, start fresh
                print(f"Warning: Could not load saved events ({error}). Starting fresh.")
                self.events = []
        else:
            print("No existing calendar data found. Starting with empty calendar.")
    
    def save_events(self):
        """
        Save all events to the JSON file.
        
        This is called after any change to ensure data persistence.
        """
        with open(self.DATA_FILE, "w") as file:
            # Convert all events to dictionaries for JSON serialization
            data = [event.to_dict() for event in self.events]
            json.dump(data, file, indent=2)
    
    def add_event(self, title, start_time, end_time):
        """
        Add a new event to the calendar if it doesn't conflict with existing events.
        
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
        
        # Check if this event overlaps with any existing event
        for existing_event in self.events:
            if new_event.overlaps_with(existing_event):
                conflict_start = existing_event.start_time.strftime('%I:%M %p')
                conflict_end = existing_event.end_time.strftime('%I:%M %p')
                return False, f"Error: This event overlaps with '{existing_event.title}' ({conflict_start} - {conflict_end})"
        
        # No conflicts found, add the event
        self.events.append(new_event)
        self.save_events()
        return True, f"Event '{title}' added successfully!"
    
    def get_events_for_date(self, target_date):
        """
        Get all events scheduled for a specific date.
        
        Args:
            target_date (date): The date to check
            
        Returns:
            list: List of Event objects for that date, sorted by start time
        """
        matching_events = []
        
        for event in self.events:
            # Check if the event's start date matches our target date
            if event.start_time.date() == target_date:
                matching_events.append(event)
        
        # Sort events by their start time so they appear in chronological order
        matching_events.sort(key=lambda e: e.start_time)
        return matching_events
    
    def get_remaining_events_today(self):
        """
        Get events that haven't started yet or are currently in progress today.
        
        This is useful for seeing what's left on your schedule.
        
        Returns:
            list: List of Event objects that are remaining today
        """
        now = datetime.now()
        today = now.date()
        
        remaining_events = []
        
        for event in self.events:
            # Event is "remaining" if it's today and hasn't ended yet
            if event.start_time.date() == today and event.end_time > now:
                remaining_events.append(event)
        
        # Sort by start time
        remaining_events.sort(key=lambda e: e.start_time)
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
        
        Args:
            event_index (int): The index of the event in that day's list (1-based)
            target_date (date): The date of the event
            
        Returns:
            tuple: (success: bool, message: str) indicating result
        """
        days_events = self.get_events_for_date(target_date)
        
        # Check if the index is valid
        if event_index < 1 or event_index > len(days_events):
            return False, f"Error: Invalid event number. Please choose 1-{len(days_events)}."
        
        # Get the event to delete (convert to 0-based index)
        event_to_delete = days_events[event_index - 1]
        
        # Remove it from our main events list
        self.events.remove(event_to_delete)
        self.save_events()
        
        return True, f"Event '{event_to_delete.title}' deleted successfully!"

