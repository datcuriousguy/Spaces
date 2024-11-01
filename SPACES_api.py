"""

Though I did mention in the readme that this project is being worked on independently by me, I would still like to
bring to the forefront the work of my teammates and the effort and time they did put in while this project was our
main focus.

Kudos team :)

"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import uvicorn

app = FastAPI()

"""

The Cross-Origin-Resource-Sharing or CORS in web browsers is supposed to be a security feature, but I doubt its worth
calling it the same considering it can be bypassed with the code below.

request-response Origins, Methods, Credentials and Headers are specific parameters to each api request routed through
the browser. This add_middleware() function simply tells the browser to expect all types of Origins, Credentials, 
methods and headers for requests from http://127.0.0.1:8000/ ... name of function in api.post ...

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL Database connection configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_username',  # Update with your MySQL username
    'password': 'your_mysql_password',  # Update with your MySQL password
    'database': 'spaces_app'  # The database where "spaces" table resides
}

"""

During my internship with Litmus7, COMP350 Software Design Course at Krea University and in group projects before, I do 
remember an emphasis being placed on modular programming, where more specialized functions (as opposed to one 
"monolithic" python program) is generally favoured.

In addition, my internship at Litmus7 taught me the significance of using try-except statements to prepare for errors.

with this in mind, using a specialized function to execute a mysql command using the MYSQL_CONFIG Dictionary above.
conn acts as the open portal to the database while the cur object goes inside to execute
commands while conn "holds the door open".

The if else clause ensures that the statement is only executed if values are present for the placeholders of the
statement in question.

"""


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


"""

Instead of using a list, I assume that using a class model with datatypes would probablly return an error if a 
data-piece of the wrong datatype was sent to the api.

classrooms is a list of strings so that there is a possibility for allowing multiple bookings in future versions,
essentially making the code slightly future-problem-proof.

Just noting that 'purpose' ensures that everyone can see the excact purpose of everyone else's bookings of a space to 
ensure full accountability. Still thinking about preventing misuse and open to suggestion.

"""


class BookingData(BaseModel):
    time_slot: str
    classrooms: list[str]
    purpose: str


"""

 book fetches the booking details entered into the textbox, selected in the set of tiles, and the purpose entered into
 a textbox on the spaces_main_booking.html webpage.
 
 for each member of the list of classrooms booked (again, for future-proofing purposes), the specific purpose of booking
 and time slot are added to the database.
 
 NOTE: I can't think of many situations where multiple bookings by
 one party are a common necessity.
 
 Satus of a booking is set to 'Booked' for a specific classroom when a booking is made.
 
Once bookings are made for all the selected classrooms in the list, the connector is commited ensuring
changes to the db are locked. The chronological timing of this hopefully makes sense - commiting the db while or
before changes are being made will increase the chance of erroneous, non-updated data being in the db.

As you can see, try-except was mass-implemnted on most functions since it seems to be known as a good practice in
coding in general.
"""


@app.post("/book")
async def book_space(data: BookingData):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        # Logging for debugging purposes
        print("Booking Details Received:")
        print(f"Time Slot: {data.time_slot}")
        print(f"Classrooms: {data.classrooms}")
        print(f"Purpose: {data.purpose}")

        # Insert the details of new booking into db
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


"""

get_available_classrooms usies a time_slot as an argument to show only the classrooms available in the selected time-
slot.

I encountered lots of trouble here due to the formatting of the timeslot being too detailed.

To fix this, the time_slot was first formatted as HH:MM thenthe first (or left) 5 characters were compared to the values 
in the database only where the status was set to 'Available'.

the else statement makes sure all classes are selected if none are found within that timeslot to prevent nothing showing
on the webpage at all. I thought this would better suit a user's tolerance than showing nothing!

"""


def get_available_classrooms(time_slot):
    print('get_available_classrooms_called')
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        print(f"Time slot passed: {time_slot}")
        # Adjusted the query to compare only the hours and minutes part... errors abound up to this point!
        cursor.execute("""
            SELECT class_room FROM spaces
            WHERE LEFT(TIME(time_slot), 5) = %s AND status = 'Available';
        """, (time_slot,))

        available_classrooms = [row[0] for row in cursor.fetchall()]

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


"""
This async (can run parallel) function uses get_available_classrooms(time_slot) as a helper function, using the timeslot
as a header in the url for an argument.
"""

# API route to get available classrooms for the selected time slot
@app.get("/available_classrooms/{time_slot}")
async def available_classrooms(time_slot: str):
    available_classrooms = get_available_classrooms(time_slot)
    print(available_classrooms)
    return {"available_classrooms": available_classrooms}


### SEE ALL BOOKINGS ###

"""
As clear by the name, this function is used to see all the bookings made along with their purposes by fetching all the
info from spaces_bookings and sending the data to the webpage, which uses a javascript for-loop to dynamically render
cool-looking tiles for each booking :)
"""

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


"""

As uvicorn is usually (from my understanding) used with asgi frameworks like fastapi, preparing for concurrent (parallel) functions is better
and has more reduncancy compared to flask's more synchronous function-handling nature.

"""
# Run the server (can use uvicorn to run)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
