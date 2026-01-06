"""
Event Module

This module contains the Event class which represents a single calendar event.
Each event has a title, start time, and end time.
"""

from datetime import datetime


class Event:
    """
    Represents a single calendar event.
    
    Each event has a title and a time range (start and end).
    Events are stored with full datetime information to support
    scheduling across multiple days.
    """
    
    def __init__(self, title, start_time, end_time):
        """
        Create a new event.
        
        Args:
            title (str): The name/description of the event
            start_time (datetime): When the event begins
            end_time (datetime): When the event ends
        """
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
    
    def overlaps_with(self, other_event):
        """
        Check if this event overlaps with another event.
        
        Two events overlap if one starts before the other ends,
        and ends after the other starts. This catches all cases:
        partial overlap, complete containment, and identical times.
        
        Args:
            other_event (Event): The event to check against
            
        Returns:
            bool: True if the events overlap, False otherwise
        """
        # Events overlap if: this starts before other ends AND this ends after other starts
        return (self.start_time < other_event.end_time and 
                self.end_time > other_event.start_time)
    
    def to_dict(self):
        """
        Convert the event to a dictionary for JSON storage.
        
        Returns:
            dict: Event data with datetime converted to ISO format strings
        """
        return {
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Event from a dictionary (loaded from JSON).
        
        Args:
            data (dict): Dictionary containing event data
            
        Returns:
            Event: A new Event instance
        """
        return cls(
            title=data["title"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"])
        )
    
    def __str__(self):
        """
        Create a human-readable string representation of the event.
        
        Returns:
            str: Formatted event details
        """
        date_str = self.start_time.strftime("%Y-%m-%d")
        start_str = self.start_time.strftime("%I:%M %p")
        end_str = self.end_time.strftime("%I:%M %p")
        return f"{self.title}: {date_str} from {start_str} to {end_str}"

