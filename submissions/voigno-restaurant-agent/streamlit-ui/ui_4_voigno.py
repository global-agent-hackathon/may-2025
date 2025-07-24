import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# Set page config
st.set_page_config(page_title="Restaurant Booking System", layout="wide")


# MongoDB connection
@st.cache_resource
def get_database():
    try:
        # MongoDB Atlas connection credentials
        username = "username"
        password = "password"

        # Encode the username and password
        encoded_username = urllib.parse.quote_plus(username)
        encoded_password = urllib.parse.quote_plus(password)

        # MongoDB Atlas connection string
        mdb_connection_string = f"mongodb+srv://{encoded_username}:{encoded_password}@mongouri"

        # Connect to MongoDB Atlas
        client = MongoClient(mdb_connection_string)
        db = client["restaurant_booking"]
        return db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None


# Initialize database connection
db = get_database()


# Helper functions
def get_collection_name(date):
    """Convert date to collection name in YYYYMMDD format"""
    return date.strftime("%Y%m%d")


def get_available_slots(collection_name):
    """Get available slots from the database"""
    if db is None:
        return []

    collection = db[collection_name]
    slots = list(collection.find({}))
    return slots


def initialize_collection_for_date(date):
    """Initialize collection for a specific date if it doesn't exist"""
    if db is None:
        return False

    collection_name = get_collection_name(date)

    # Check if collection exists and has data
    if (
        collection_name in db.list_collection_names()
        and db[collection_name].count_documents({}) > 0
    ):
        return True

    # Define tables
    tables = {
        "A": {
            "size": 4,
            "location": "window",
            "description": "Window table with city view",
        },
        "B": {"size": 4, "location": "aisle", "description": "Central aisle table"},
        "C": {"size": 4, "location": "corner", "description": "Quiet corner table"},
        "D": {"size": 6, "location": "patio", "description": "Outdoor patio table"},
        "E": {"size": 4, "location": "bar", "description": "Near the bar"},
    }

    # Define time slots
    time_slots = [
        "9:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
    ]

    # Create collection
    collection = db[collection_name]

    # Initialize documents
    documents = []
    for time in time_slots:
        for table_id, table_info in tables.items():
            slot_id = f"{time.replace(':', '')}t{table_id}"
            document = {
                "slot_id": slot_id,
                "time": time,
                "table": table_id,
                "table_size": table_info["size"],
                "table_location": table_info["location"],
                "table_description": table_info["description"],
                "available": True,
                "customer_phone": None,
                "party_size": None,
                "special_requests": None,
            }
            documents.append(document)

    # Insert documents
    if documents:
        collection.insert_many(documents)
        return True

    return False


def create_table_visualization(slots_data, selected_time):
    """Create a visual representation of tables and their availability"""
    # Filter for selected time
    time_slots = [slot for slot in slots_data if slot["time"] == selected_time]

    # Define table positions (x, y)
    table_positions = {
        "A": (1, 3),  # Window position
        "B": (2, 2),  # Aisle position
        "C": (3, 1),  # Corner position
        "D": (1, 1),  # Patio position
        "E": (3, 3),  # Bar position
    }

    # Create figure
    fig = go.Figure()

    # Add tables to the figure
    for slot in time_slots:
        table_id = slot["table"]
        x, y = table_positions[table_id]

        # Set color based on availability
        color = "green" if slot["available"] else "red"

        # Create table visualization
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    symbol="square",
                    size=50,
                    color=color,
                    line=dict(width=2, color="black"),
                ),
                text=[table_id],
                textposition="middle center",
                textfont=dict(size=16, color="white"),
                hoverinfo="text",
                hovertext=[
                    f"Table {table_id}: {slot['table_description']}<br>Size: {slot['table_size']} people<br>Location: {slot['table_location']}<br>Status: {'Available' if slot['available'] else 'Booked'}"
                ],
            )
        )

    # Update layout
    fig.update_layout(
        width=600,
        height=400,
        title=f"Table Availability at {selected_time}",
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(
            range=[0, 4],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            range=[0, 4],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
    )

    # Add simple annotations for orientation without rectangles
    fig.add_annotation(x=1, y=3.3, text="Window", showarrow=False, font=dict(size=10))
    fig.add_annotation(x=1, y=0.7, text="Patio", showarrow=False, font=dict(size=10))
    fig.add_annotation(x=3, y=3.3, text="Bar", showarrow=False, font=dict(size=10))

    return fig


def book_table(collection_name, slot_id, customer_phone, party_size, special_requests):
    """Book a table by updating its availability status"""
    if db is None:
        return False

    collection = db[collection_name]

    # Update document
    result = collection.update_one(
        {"slot_id": slot_id},
        {
            "$set": {
                "available": False,
                "customer_phone": customer_phone,
                "party_size": party_size,
                "special_requests": special_requests,
            }
        },
    )

    return result.modified_count > 0


def cancel_booking(collection_name, slot_id):
    """Cancel a booking by updating its availability status"""
    if db is None:
        return False

    collection = db[collection_name]

    # Update document
    result = collection.update_one(
        {"slot_id": slot_id},
        {
            "$set": {
                "available": True,
                "customer_phone": None,
                "party_size": None,
                "special_requests": None,
            }
        },
    )

    return result.modified_count > 0


# UI Components
st.title("Restaurant Booking System")

# Sidebar for date selection and admin options
with st.sidebar:
    st.header("Select Date")
    today = datetime.now().date()
    selected_date = st.date_input(
        "Booking Date", today, min_value=today, max_value=today + timedelta(days=30)
    )

    st.header("Admin Area")
    if st.button("Initialize Today's Data"):
        if initialize_collection_for_date(today):
            st.success(f"Initialized data for {today}")
        else:
            st.error("Failed to initialize data")

# Main content
col1, col2 = st.columns([1, 2])

# Initialize collection for selected date
collection_name = get_collection_name(selected_date)
initialize_status = initialize_collection_for_date(selected_date)
if not initialize_status:
    st.warning(f"No data available for {selected_date}. Please initialize the data.")

# Fetch available slots
slots_data = get_available_slots(collection_name)

with col1:
    st.header("Make a Reservation")

    # Convert to pandas DataFrame for easier filtering
    if slots_data:
        slots_df = pd.DataFrame(slots_data)

        # Get unique time slots from the data
        available_times = sorted(slots_df["time"].unique().tolist())

        # Time selection
        selected_time = st.selectbox("Select Time", available_times)

        # Filter slots for selected time
        time_slots_df = slots_df[slots_df["time"] == selected_time]

        # Table selection
        available_tables = time_slots_df[time_slots_df["available"]]["table"].tolist()
        if available_tables:
            selected_table = st.selectbox("Select Table", available_tables)

            # Get selected slot info
            selected_slot = time_slots_df[
                time_slots_df["table"] == selected_table
            ].iloc[0]
            selected_slot_id = selected_slot["slot_id"]

            # Display table info
            st.write("**Table Information:**")
            st.write(f"- Size: {selected_slot['table_size']} people")
            st.write(f"- Location: {selected_slot['table_location']}")
            st.write(f"- Description: {selected_slot['table_description']}")

            # Customer information form
            st.subheader("Customer Information")
            customer_phone = st.text_input("Phone Number")
            party_size = st.number_input(
                "Party Size",
                min_value=1,
                max_value=selected_slot["table_size"],
                value=2,
            )
            special_requests = st.text_area("Special Requests", height=100)

            # Book button
            if st.button("Book Table"):
                if book_table(
                    collection_name,
                    selected_slot_id,
                    customer_phone,
                    party_size,
                    special_requests,
                ):
                    st.success(
                        f"Table {selected_table} booked successfully for {selected_time} on {selected_date}"
                    )
                    st.balloons()
                    # Refresh page to update data
                    st.rerun()
                else:
                    st.error("Failed to book table")
        else:
            st.warning(f"No tables available for {selected_time}")
    else:
        st.warning("No data available for selected date")

with col2:
    st.header("Table Availability")

    if slots_data:
        # Create tables visualization
        available_times = sorted(pd.DataFrame(slots_data)["time"].unique().tolist())
        selected_time_viz = st.selectbox(
            "Select Time to View", available_times, key="time_viz"
        )

        # Show tables visualization
        table_fig = create_table_visualization(slots_data, selected_time_viz)
        st.plotly_chart(table_fig)

        # Show booking list
        st.subheader("Current Bookings")
        bookings_df = pd.DataFrame(slots_data)
        bookings_df = bookings_df[~bookings_df["available"]]

        if not bookings_df.empty:
            # Format booking data for display
            display_df = bookings_df[
                [
                    "time",
                    "table",
                    "table_size",
                    "customer_phone",
                    "party_size",
                    "special_requests",
                ]
            ]
            display_df = display_df.rename(
                columns={
                    "time": "Time",
                    "table": "Table",
                    "table_size": "Table Size",
                    "customer_phone": "Phone",
                    "party_size": "Party Size",
                    "special_requests": "Requests",
                }
            )
            st.dataframe(display_df, use_container_width=True)

            # Cancel booking option
            st.subheader("Cancel Booking")
            booked_slots = bookings_df["slot_id"].tolist()
            booked_tables = (
                bookings_df[["slot_id", "table", "time"]]
                .apply(lambda row: f"Table {row['table']} at {row['time']}", axis=1)
                .tolist()
            )

            # Create a dictionary to map display names to slot_ids
            booking_options = dict(zip(booked_tables, booked_slots))

            # If there are bookings, show the cancel option
            if booking_options:
                selected_booking = st.selectbox(
                    "Select booking to cancel", list(booking_options.keys())
                )
                selected_booking_id = booking_options[selected_booking]

                if st.button("Cancel Booking"):
                    if cancel_booking(collection_name, selected_booking_id):
                        st.success(
                            f"Booking for {selected_booking} cancelled successfully"
                        )
                        # Refresh page to update data
                        st.rerun()
                    else:
                        st.error("Failed to cancel booking")
        else:
            st.info("No bookings for this date yet")
