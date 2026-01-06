"""
Unit Tests for the Calendar Application

This file contains tests to verify that the Event and Calendar classes
work correctly. Run these tests with: python -m unittest test_calendar.py

These tests cover:
- Event overlap detection (the core logic)
- Adding events to the calendar
- Preventing overlapping events
- Retrieving events for a specific date
- Finding available time slots
- Data serialization (converting to/from JSON format)
"""

import unittest
import os
from datetime import datetime, date, timedelta

from event import Event
from calendar_manager import Calendar


class TestEventOverlap(unittest.TestCase):
    """
    Tests for the Event.overlaps_with() method.
    
    This is the most critical piece of logic in the application.
    We test various overlap scenarios to make sure it catches all cases.
    """
    
    def test_events_that_overlap_partially(self):
        """
        Test when one event starts before another ends.
        
        Event A: 9:00 AM - 10:00 AM
        Event B: 9:30 AM - 10:30 AM
        These should overlap.
        """
        event_a = Event(
            "Meeting A",
            datetime(2026, 1, 15, 9, 0),   # 9:00 AM
            datetime(2026, 1, 15, 10, 0)   # 10:00 AM
        )
        event_b = Event(
            "Meeting B",
            datetime(2026, 1, 15, 9, 30),  # 9:30 AM
            datetime(2026, 1, 15, 10, 30)  # 10:30 AM
        )
        
        # Both directions should detect the overlap
        self.assertTrue(event_a.overlaps_with(event_b))
        self.assertTrue(event_b.overlaps_with(event_a))
    
    def test_event_completely_inside_another(self):
        """
        Test when one event is entirely within another.
        
        Event A: 9:00 AM - 12:00 PM (3 hours)
        Event B: 10:00 AM - 11:00 AM (inside A)
        These should overlap.
        """
        event_a = Event(
            "Long Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 12, 0)
        )
        event_b = Event(
            "Short Meeting",
            datetime(2026, 1, 15, 10, 0),
            datetime(2026, 1, 15, 11, 0)
        )
        
        self.assertTrue(event_a.overlaps_with(event_b))
        self.assertTrue(event_b.overlaps_with(event_a))
    
    def test_identical_events_overlap(self):
        """
        Test when two events have the exact same start and end times.
        These should definitely overlap.
        """
        event_a = Event(
            "Meeting A",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        event_b = Event(
            "Meeting B",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        self.assertTrue(event_a.overlaps_with(event_b))
    
    def test_adjacent_events_do_not_overlap(self):
        """
        Test when one event ends exactly when another begins.
        
        Event A: 9:00 AM - 10:00 AM
        Event B: 10:00 AM - 11:00 AM
        These should NOT overlap (back-to-back meetings are allowed).
        """
        event_a = Event(
            "First Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        event_b = Event(
            "Second Meeting",
            datetime(2026, 1, 15, 10, 0),
            datetime(2026, 1, 15, 11, 0)
        )
        
        # Adjacent events should NOT overlap
        self.assertFalse(event_a.overlaps_with(event_b))
        self.assertFalse(event_b.overlaps_with(event_a))
    
    def test_completely_separate_events_do_not_overlap(self):
        """
        Test when events are hours apart.
        
        Event A: 9:00 AM - 10:00 AM
        Event B: 2:00 PM - 3:00 PM
        These should NOT overlap.
        """
        event_a = Event(
            "Morning Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        event_b = Event(
            "Afternoon Meeting",
            datetime(2026, 1, 15, 14, 0),
            datetime(2026, 1, 15, 15, 0)
        )
        
        self.assertFalse(event_a.overlaps_with(event_b))
        self.assertFalse(event_b.overlaps_with(event_a))
    
    def test_events_on_different_days_do_not_overlap(self):
        """
        Test that events on different days don't overlap,
        even if they have the same times.
        """
        event_a = Event(
            "Monday Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        event_b = Event(
            "Tuesday Meeting",
            datetime(2026, 1, 16, 9, 0),
            datetime(2026, 1, 16, 10, 0)
        )
        
        self.assertFalse(event_a.overlaps_with(event_b))


class TestEventSerialization(unittest.TestCase):
    """
    Tests for converting Event objects to/from dictionaries.
    This is important for JSON storage to work correctly.
    """
    
    def test_event_to_dict(self):
        """Test that an event converts to a dictionary correctly."""
        event = Event(
            "Team Standup",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 9, 30)
        )
        
        result = event.to_dict()
        
        self.assertEqual(result["title"], "Team Standup")
        self.assertEqual(result["start_time"], "2026-01-15T09:00:00")
        self.assertEqual(result["end_time"], "2026-01-15T09:30:00")
    
    def test_event_from_dict(self):
        """Test that an event can be recreated from a dictionary."""
        data = {
            "title": "Project Review",
            "start_time": "2026-01-15T14:00:00",
            "end_time": "2026-01-15T15:00:00"
        }
        
        event = Event.from_dict(data)
        
        self.assertEqual(event.title, "Project Review")
        self.assertEqual(event.start_time, datetime(2026, 1, 15, 14, 0))
        self.assertEqual(event.end_time, datetime(2026, 1, 15, 15, 0))
    
    def test_round_trip_serialization(self):
        """
        Test that converting to dict and back preserves all data.
        This simulates saving to JSON and loading it back.
        """
        original = Event(
            "Important Meeting",
            datetime(2026, 1, 15, 10, 30),
            datetime(2026, 1, 15, 11, 45)
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Event.from_dict(data)
        
        # All properties should match
        self.assertEqual(restored.title, original.title)
        self.assertEqual(restored.start_time, original.start_time)
        self.assertEqual(restored.end_time, original.end_time)


class TestCalendar(unittest.TestCase):
    """
    Tests for the Calendar class.
    
    These tests use a separate test data file to avoid
    interfering with actual calendar data.
    """
    
    def setUp(self):
        """
        Set up a fresh calendar for each test.
        We use a different data file so tests don't affect real data.
        """
        # Use a test-specific data file
        Calendar.DATA_FILE = "test_calendar_data.json"
        
        # Remove any existing test data file
        if os.path.exists(Calendar.DATA_FILE):
            os.remove(Calendar.DATA_FILE)
        
        # Create a fresh calendar
        self.calendar = Calendar()
    
    def tearDown(self):
        """Clean up the test data file after each test."""
        if os.path.exists(Calendar.DATA_FILE):
            os.remove(Calendar.DATA_FILE)
    
    def test_add_event_success(self):
        """Test that a valid event can be added."""
        success, message = self.calendar.add_event(
            "Team Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        self.assertTrue(success)
        self.assertIn("successfully", message.lower())
        self.assertEqual(len(self.calendar.events), 1)
    
    def test_add_event_rejects_end_before_start(self):
        """Test that an event with end time before start time is rejected."""
        success, message = self.calendar.add_event(
            "Invalid Meeting",
            datetime(2026, 1, 15, 10, 0),  # Start at 10:00
            datetime(2026, 1, 15, 9, 0)    # End at 9:00 (invalid!)
        )
        
        self.assertFalse(success)
        self.assertIn("error", message.lower())
        self.assertEqual(len(self.calendar.events), 0)
    
    def test_add_event_rejects_overlapping_event(self):
        """Test that overlapping events are prevented."""
        # Add the first event
        self.calendar.add_event(
            "First Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        # Try to add an overlapping event
        success, message = self.calendar.add_event(
            "Overlapping Meeting",
            datetime(2026, 1, 15, 9, 30),
            datetime(2026, 1, 15, 10, 30)
        )
        
        self.assertFalse(success)
        self.assertIn("overlap", message.lower())
        self.assertEqual(len(self.calendar.events), 1)  # Only first event exists
    
    def test_add_event_allows_adjacent_events(self):
        """Test that back-to-back events are allowed."""
        # Add first event
        self.calendar.add_event(
            "First Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        # Add adjacent event (starts when first ends)
        success, message = self.calendar.add_event(
            "Second Meeting",
            datetime(2026, 1, 15, 10, 0),
            datetime(2026, 1, 15, 11, 0)
        )
        
        self.assertTrue(success)
        self.assertEqual(len(self.calendar.events), 2)
    
    def test_get_events_for_date(self):
        """Test retrieving events for a specific date."""
        # Add events on different days
        self.calendar.add_event(
            "Monday Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        self.calendar.add_event(
            "Tuesday Meeting",
            datetime(2026, 1, 16, 9, 0),
            datetime(2026, 1, 16, 10, 0)
        )
        
        # Get events for Monday only
        monday_events = self.calendar.get_events_for_date(date(2026, 1, 15))
        
        self.assertEqual(len(monday_events), 1)
        self.assertEqual(monday_events[0].title, "Monday Meeting")
    
    def test_get_events_for_date_returns_sorted(self):
        """Test that events are returned in chronological order."""
        # Add events out of order
        self.calendar.add_event(
            "Afternoon Meeting",
            datetime(2026, 1, 15, 14, 0),
            datetime(2026, 1, 15, 15, 0)
        )
        self.calendar.add_event(
            "Morning Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        events = self.calendar.get_events_for_date(date(2026, 1, 15))
        
        # Morning meeting should come first
        self.assertEqual(events[0].title, "Morning Meeting")
        self.assertEqual(events[1].title, "Afternoon Meeting")
    
    def test_get_events_for_date_empty(self):
        """Test that an empty list is returned when no events exist."""
        events = self.calendar.get_events_for_date(date(2026, 1, 15))
        
        self.assertEqual(events, [])
    
    def test_find_available_slot_empty_calendar(self):
        """Test finding a slot when the calendar is empty."""
        slot = self.calendar.find_next_available_slot(
            60,  # 60 minutes
            date(2026, 1, 15)
        )
        
        # Should find a slot starting at 8:00 AM (start of business hours)
        self.assertIsNotNone(slot)
        start, end = slot
        self.assertEqual(start.hour, 8)
        self.assertEqual(start.minute, 0)
    
    def test_find_available_slot_between_events(self):
        """Test finding a slot in a gap between two events."""
        # Add morning event: 8:00 - 9:00
        self.calendar.add_event(
            "Early Meeting",
            datetime(2026, 1, 15, 8, 0),
            datetime(2026, 1, 15, 9, 0)
        )
        
        # Add afternoon event: 11:00 - 12:00
        self.calendar.add_event(
            "Late Meeting",
            datetime(2026, 1, 15, 11, 0),
            datetime(2026, 1, 15, 12, 0)
        )
        
        # Look for a 60-minute slot
        slot = self.calendar.find_next_available_slot(60, date(2026, 1, 15))
        
        # Should find the gap from 9:00 - 10:00
        self.assertIsNotNone(slot)
        start, end = slot
        self.assertEqual(start.hour, 9)
    
    def test_find_available_slot_no_room(self):
        """Test when no slot is available (day is fully booked)."""
        # Book the entire day from 8 AM to 6 PM
        self.calendar.add_event(
            "All Day Event",
            datetime(2026, 1, 15, 8, 0),
            datetime(2026, 1, 15, 18, 0)
        )
        
        # Try to find any slot
        slot = self.calendar.find_next_available_slot(30, date(2026, 1, 15))
        
        self.assertIsNone(slot)
    
    def test_delete_event(self):
        """Test deleting an event from the calendar."""
        # Add an event
        self.calendar.add_event(
            "Meeting to Delete",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        # Delete it
        success, message = self.calendar.delete_event(1, date(2026, 1, 15))
        
        self.assertTrue(success)
        self.assertEqual(len(self.calendar.events), 0)
    
    def test_delete_event_invalid_index(self):
        """Test that deleting with an invalid index fails gracefully."""
        # Add one event
        self.calendar.add_event(
            "Only Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        # Try to delete event #5 (doesn't exist)
        success, message = self.calendar.delete_event(5, date(2026, 1, 15))
        
        self.assertFalse(success)
        self.assertIn("invalid", message.lower())
        self.assertEqual(len(self.calendar.events), 1)  # Event still exists
    
    def test_data_persistence(self):
        """Test that events are saved and can be reloaded."""
        # Add an event
        self.calendar.add_event(
            "Persistent Meeting",
            datetime(2026, 1, 15, 9, 0),
            datetime(2026, 1, 15, 10, 0)
        )
        
        # Create a new calendar instance (simulates restarting the app)
        new_calendar = Calendar()
        
        # The event should still be there
        self.assertEqual(len(new_calendar.events), 1)
        self.assertEqual(new_calendar.events[0].title, "Persistent Meeting")


# This allows running the tests directly with: python test_calendar.py
if __name__ == "__main__":
    # Run all tests with verbose output
    unittest.main(verbosity=2)

