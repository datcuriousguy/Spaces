from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import uvicorn

# Create FastAPI app
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this according to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL Database connection configuration
MYSQL_CONFIG = {
    'host': 'localhost',  # Update with your MySQL server address
    'user': 'your_mysql_username',  # Update with your MySQL user
    'password': 'your_mysql_password',  # Update with your MySQL password
    'database': 'spaces_app'  # The database where the "spaces" table resides
}


# Function to execute a MySQL statement
def execute_sql(statement, values=None):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        if values:
            cursor.execute(statement, values)
        else:
            cursor.execute(statement)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error executing SQL: {e}")


# Define request body model using Pydantic
class BookingData(BaseModel):
    time_slot: str
    classrooms: list[str]
    purpose: str


# API route to handle booking data
@app.post("/book")
async def book_space(data: BookingData):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        # Log the data to the console
        print("Booking Details Received:")
        print(f"Time Slot: {data.time_slot}")
        print(f"Classrooms: {data.classrooms}")
        print(f"Purpose: {data.purpose}")

        # Insert booking details into the database
        for classroom in data.classrooms:
            cursor.execute("""
                UPDATE spaces
                SET status = 'Booked', purpose = %s
                WHERE class_room = %s AND time_slot = %s;
            """, (data.purpose, classroom, data.time_slot))

            cursor.execute('''
                        INSERT INTO spaces_bookings (time_slot, classroom, purpose)
                        VALUES (%s, %s, %s)
                    ''', (data.time_slot, classroom, data.purpose))
            print('bookings db updated.')

        conn.commit()

        # Send back the booking details as a response (to display on the webpage)
        response_data = {
            "message": "Booking received successfully!",
            "time_slot": data.time_slot,
            "classrooms": data.classrooms,
            "purpose": data.purpose
        }

        cursor.close()
        conn.close()
    except Error as e:
        return {"error": str(e)}

    return response_data


# Function to get available classrooms based on time slot
def get_available_classrooms(time_slot):
    print('get_available_classrooms_called')
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        print(f"Time slot passed: {time_slot}")
        # Adjust the query to compare only the hours and minutes part
        cursor.execute("""
            SELECT class_room FROM spaces
            WHERE LEFT(TIME(time_slot), 5) = %s AND status = 'Available';
        """, (time_slot,))

        # Fetch all the rows that match the query
        available_classrooms = [row[0] for row in cursor.fetchall()]

        # Check if any classrooms are found
        if available_classrooms:
            print(f"Classrooms for time_slot '{time_slot}':")
            for classroom in available_classrooms:
                print(classroom)
        else:
            print(f"No classrooms found for the time_slot '{time_slot}'")
            available_classrooms = cursor.execute("""
                SELECT class_room FROM spaces;
            """).fetchall()
            return available_classrooms

        cursor.close()
        conn.close()
        if available_classrooms:
            return available_classrooms
        else:

            cursor.execute("""
                        SELECT class_room FROM spaces;
                    """)
            # Fetch all the rows that match the query
            available_classrooms = [row[0] for row in cursor.fetchall()]
            print('No classrooms for this slot:\n', available_classrooms)

            return available_classrooms
    except mysql.connector.Error as e:
        print(f"Error fetching available classrooms: {e}")
        return []


# API route to get available classrooms for the selected time slot
@app.get("/available_classrooms/{time_slot}")
async def available_classrooms(time_slot: str):
    available_classrooms = get_available_classrooms(time_slot)
    print(available_classrooms)
    return {"available_classrooms": available_classrooms}


### SEE ALL BOOKINGS ###

@app.get('/see_bookings')
def see_bookings():
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",
        password="your_mysql_password",
        database="spaces_app"
    )

    cursor = conn.cursor(dictionary=True)

    # Query to get all bookings
    query = "SELECT classroom, time_slot, purpose FROM spaces_bookings"
    cursor.execute(query)

    # Fetch all the rows from the table
    bookings = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    from flask import jsonify
    # Return the bookings data as JSON
    print(bookings)
    return bookings


# Run the server (can use uvicorn to run)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
