from typing import Dict, Any
from datetime import datetime, timedelta
from pymongo import MongoClient

from agno.tools.toolkit import Toolkit


class RestaurantBookingToolkit(Toolkit):
    def __init__(self, mongo_uri: str, db_name: str = "restaurant_booking"):
        """Initialize parameters: mongo_uri (str), db_name (str, optional)"""
        super().__init__(name="restaurant_booking")

        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]

            # Register all functions with the toolkit
            self.register(self.book_table)
            self.register(self.find_available_tables)
            self.register(self.find_available_time_slots)
            self.register(self.cancel_booking)
            self.register(self.find_customer_bookings)
            self.register(self.get_all_bookings)
            self.register(self.check_availability_across_days)

        except Exception as e:
            raise Exception(
                f"Database connection error: {str(e)}. Parameters: mongo_uri (str), db_name (str, optional)"
            )

    def get_collection_name(self, date: datetime) -> str:
        """Get the collection name for a specific date"""
        return date.strftime("%Y%m%d")

    def ensure_date_collection(self, date: datetime) -> Dict[str, Any]:
        """Check if collection exists for date"""
        collection_name = self.get_collection_name(date)
        if collection_name not in self.db.list_collection_names():
            return {
                "success": False,
                "message": f"No collection exists for date {date.strftime('%Y-%m-%d')}",
            }
        return {"success": True, "date": date}

    def book_table(
        self,
        date: str,
        slot_id: str,
        customer_phone: str,
        party_size: int,
        special_requests: str = None,
    ) -> str:
        """Book a table with parameters: date (YYYY-MM-DD), slot_id (HHMMtX), customer_phone (str), party_size (int), special_requests (str, optional)"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_check = self.ensure_date_collection(date_obj)
            if not date_check["success"]:
                return f"{date_check['message']}. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX), customer_phone (str), party_size (int), special_requests (str, optional)"

            collection_name = self.get_collection_name(date_obj)
            date_collection = self.db[collection_name]

            # Check if the slot is available
            slot = date_collection.find_one({"slot_id": slot_id})
            if not slot:
                return f"Invalid slot: {slot_id}. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX), customer_phone (str), party_size (int), special_requests (str, optional)"

            if not slot["available"]:
                return f"The table {slot['table']} is already booked for {slot['time']}"

            if party_size > slot["table_size"]:
                return f"Party size {party_size} exceeds table capacity of {slot['table_size']}"

            result = date_collection.update_one(
                {"slot_id": slot_id, "available": True},
                {
                    "$set": {
                        "available": False,
                        "customer_phone": customer_phone,
                        "party_size": party_size,
                        "special_requests": special_requests,
                        "booked_at": datetime.now(),
                    }
                },
            )

            if result.modified_count == 1:
                return f"Successfully booked table {slot['table']} ({slot['table_location']}) at {slot['time']} on {date}. Booking reference: {slot_id}"
            else:
                return "Could not book the slot. It may have been taken just now."

        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD format. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX), customer_phone (str), party_size (int), special_requests (str, optional){e}"
        except Exception as e:
            return f"Error booking table: {str(e)}. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX), customer_phone (str), party_size (int), special_requests (str, optional)"

    def find_available_tables(
        self, date: str, time_slot: str, location: str = None
    ) -> str:
        """Find tables with parameters: date (YYYY-MM-DD), time_slot (HH:MM, HHMM, or with AM/PM), location (str, optional)"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")

            # Handle various time formats
            try:
                if time_slot.isdigit() and len(time_slot) == 4:
                    time_slot = f"{time_slot[:2]}:{time_slot[2:]}"
                elif any(suffix in time_slot.lower() for suffix in ["am", "pm"]):
                    clean_time = time_slot.lower().replace(" ", "")
                    time_obj = datetime.strptime(clean_time, "%I%p")
                    time_slot = time_obj.strftime("%H:%M")
                elif ":" in time_slot:
                    datetime.strptime(time_slot, "%H:%M")
                else:
                    return "Invalid time format. Please provide time in HH:MM, HHMM, or with AM/PM indicator. Parameters: date (YYYY-MM-DD), time_slot (HH:MM, HHMM, or with AM/PM), location (str, optional)"
            except ValueError:
                return "Invalid time format. Please provide time in HH:MM, HHMM, or with AM/PM indicator. Parameters: date (YYYY-MM-DD), time_slot (HH:MM, HHMM, or with AM/PM), location (str, optional)"

            date_check = self.ensure_date_collection(date_obj)
            if not date_check["success"]:
                return f"{date_check['message']}. Parameters: date (YYYY-MM-DD), time_slot (HH:MM, HHMM, or with AM/PM), location (str, optional)"

            collection_name = self.get_collection_name(date_obj)
            date_collection = self.db[collection_name]

            query = {"time": time_slot, "available": True}
            if location:
                query["table_location"] = location

            available_slots = list(date_collection.find(query))

            if not available_slots:
                return f"No available tables found for {date} at {time_slot}"

            result = f"Available tables for {date} at {time_slot}:\n"
            for slot in available_slots:
                result += f"Table {slot['table']} - {slot['table_location']}, Capacity: {slot['table_size']} slot_id:{slot['slot_id']}\n"

            return result

        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD format. Parameters: date (YYYY-MM-DD), time_slot (HH:MM, HHMM, or with AM/PM), location (str, optional){e}"
        except Exception as e:
            return f"Error finding available tables: {str(e)}. Parameters: date (YYYY-MM-DD), time_slot (HH:MM, HHMM, or with AM/PM), location (str, optional)"

    def find_available_time_slots(
        self, date: str, party_size: int = None, location: str = None
    ) -> str:
        """Find slots with parameters: date (YYYY-MM-DD), party_size (int, optional), location (str, optional)"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_check = self.ensure_date_collection(date_obj)
            if not date_check["success"]:
                return f"{date_check['message']}. Parameters: date (YYYY-MM-DD), party_size (int, optional), location (str, optional)"

            collection_name = self.get_collection_name(date_obj)
            date_collection = self.db[collection_name]

            query = {"available": True}
            if party_size:
                query["table_size"] = {"$gte": party_size}
            if location:
                query["table_location"] = location

            available_slots = list(date_collection.find(query))

            if not available_slots:
                location_text = f" in the {location} area" if location else ""
                party_text = f" for a party of {party_size}" if party_size else ""
                return f"No available time slots found for {date}{location_text}{party_text}"

            availability_by_time = {}
            for slot in available_slots:
                time = slot["time"]
                if time not in availability_by_time:
                    availability_by_time[time] = []
                availability_by_time[time].append(
                    {
                        "table": slot["table"],
                        "size": slot["table_size"],
                        "location": slot["table_location"],
                    }
                )

            sorted_times = sorted(availability_by_time.keys())
            location_text = f" in the {location} area" if location else ""
            party_text = f" for a party of {party_size}" if party_size else ""
            result = f"Available time slots for {date}{location_text}{party_text}:\n"

            for time in sorted_times:
                tables = availability_by_time[time]
                result += f"{time}: {len(tables)} table(s) available\n"

            return result

        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD format. Parameters: date (YYYY-MM-DD), party_size (int, optional), location (str, optional){e}"
        except Exception as e:
            return f"Error finding available time slots: {str(e)}. Parameters: date (YYYY-MM-DD), party_size (int, optional), location (str, optional)"

    def cancel_booking(self, date: str, slot_id: str) -> str:
        """Cancel booking with parameters: date (YYYY-MM-DD), slot_id (HHMMtX)"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_check = self.ensure_date_collection(date_obj)
            if not date_check["success"]:
                return f"{date_check['message']}. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX)"

            collection_name = self.get_collection_name(date_obj)
            date_collection = self.db[collection_name]

            slot = date_collection.find_one({"slot_id": slot_id, "available": False})
            if not slot:
                return f"No booking found for slot {slot_id} on {date}"

            result = date_collection.update_one(
                {"slot_id": slot_id},
                {
                    "$set": {
                        "available": True,
                        "customer_phone": None,
                        "party_size": None,
                        "special_requests": None,
                        "cancelled_at": datetime.now(),
                    }
                },
            )

            if result.modified_count == 1:
                return f"Successfully cancelled booking for {slot_id} on {date}"
            else:
                return "Could not cancel the booking"

        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD format. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX){e}"
        except Exception as e:
            return f"Error cancelling booking: {str(e)}. Parameters: date (YYYY-MM-DD), slot_id (HHMMtX)"

    def find_customer_bookings(
        self, customer_phone: str, specific_date: str = None
    ) -> str:
        """Find bookings with parameters: customer_phone (str), specific_date (YYYY-MM-DD, optional)"""
        try:
            all_bookings = []

            if specific_date:
                date_obj = datetime.strptime(specific_date, "%Y-%m-%d")
                date_check = self.ensure_date_collection(date_obj)
                if not date_check["success"]:
                    return f"{date_check['message']}. Parameters: customer_phone (str), specific_date (YYYY-MM-DD, optional)"

                collection_name = self.get_collection_name(date_obj)
                date_collection = self.db[collection_name]

                bookings = list(
                    date_collection.find(
                        {"customer_phone": customer_phone, "available": False}
                    )
                )

                for booking in bookings:
                    all_bookings.append(
                        {
                            "date": specific_date,
                            "table": booking["table"],
                            "time": booking["time"],
                            "party_size": booking["party_size"],
                            "location": booking["table_location"],
                            "slot_id": booking["slot_id"],
                        }
                    )
            else:
                today = datetime.now()
                today = datetime(today.year, today.month, today.day)
                all_collections = set(self.db.list_collection_names())

                for i in range(60):
                    date = today + timedelta(days=i)
                    collection_name = self.get_collection_name(date)

                    if collection_name in all_collections:
                        date_collection = self.db[collection_name]
                        bookings = list(
                            date_collection.find(
                                {"customer_phone": customer_phone, "available": False}
                            )
                        )

                        for booking in bookings:
                            all_bookings.append(
                                {
                                    "date": date.strftime("%Y-%m-%d"),
                                    "table": booking["table"],
                                    "time": booking["time"],
                                    "party_size": booking["party_size"],
                                    "location": booking["table_location"],
                                    "slot_id": booking["slot_id"],
                                }
                            )

            if not all_bookings:
                date_text = (
                    f" on {specific_date}" if specific_date else " in the next 60 days"
                )
                return f"No bookings found for phone {customer_phone}{date_text}"

            all_bookings.sort(key=lambda x: (x["date"], x["time"]))
            result = f"Bookings for customer {customer_phone}:\n"
            for booking in all_bookings:
                result += f"Date: {booking['date']}, Time: {booking['time']}, Table: {booking['table']} ({booking['location']}), Party size: {booking['party_size']}, Slot_id: {booking['slot_id']}\n"

            return result

        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD format. Parameters: customer_phone (str), specific_date (YYYY-MM-DD, optional){e}"
        except Exception as e:
            return f"Error finding customer bookings: {str(e)}. Parameters: customer_phone (str), specific_date (YYYY-MM-DD, optional)"

    def get_all_bookings(self, date: str) -> str:
        """Get bookings with parameters: date (YYYY-MM-DD)"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_check = self.ensure_date_collection(date_obj)
            if not date_check["success"]:
                return f"{date_check['message']}. Parameters: date (YYYY-MM-DD)"

            collection_name = self.get_collection_name(date_obj)
            date_collection = self.db[collection_name]

            bookings = list(date_collection.find({"available": False}))

            if not bookings:
                return f"No bookings found for {date}"

            result = f"Bookings for {date}:\n"
            bookings.sort(key=lambda x: x["time"])

            for booking in bookings:
                result += f"Time: {booking['time']}, Table: {booking['table']} ({booking['table_location']}), Phone: {booking['customer_phone']}, Party size: {booking['party_size']}\n"

            return result

        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD format. Parameters: date (YYYY-MM-DD){e}"
        except Exception as e:
            return (
                f"Error getting all bookings: {str(e)}. Parameters: date (YYYY-MM-DD)"
            )

    def check_availability_across_days(
        self,
        start_date: str,
        end_date: str,
        time_slot: str,
        party_size: int = None,
        location: str = None,
    ) -> str:
        """Check availability with parameters: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), time_slot (HH:MM), party_size (int, optional), location (str, optional)"""
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

            delta = (end_date_obj - start_date_obj).days + 1
            if delta > 60:
                return "Can only check availability for up to 60 days at once"

            location_text = f" in the {location} area" if location else ""
            party_text = f" for a party of {party_size}" if party_size else ""
            result = f"Availability for {time_slot}{location_text}{party_text} between {start_date} and {end_date}:\n"

            days_with_availability = 0

            for i in range(delta):
                date = start_date_obj + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")

                collection_name = self.get_collection_name(date)
                if collection_name not in self.db.list_collection_names():
                    continue

                date_collection = self.db[collection_name]
                query = {"time": time_slot, "available": True}

                if party_size:
                    query["table_size"] = {"$gte": party_size}
                if location:
                    query["table_location"] = location

                available_slots = list(date_collection.find(query))

                if available_slots:
                    days_with_availability += 1
                    result += f"{date_str}: {len(available_slots)} table(s) available\n"

            if days_with_availability == 0:
                return f"No availability found for {time_slot}{location_text}{party_text} between {start_date} and {end_date}"

            return result

        except ValueError as e:
            return f"Invalid date or time format. Use YYYY-MM-DD for dates and HH:MM for time slot. Parameters: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), time_slot (HH:MM), party_size (int, optional), location (str, optional){e}"
        except Exception as e:
            return f"Error checking availability: {str(e)}. Parameters: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), time_slot (HH:MM), party_size (int, optional), location (str, optional)"
