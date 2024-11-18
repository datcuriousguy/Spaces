// Variables to hold selected time slot and classrooms
let selectedTimeSlot = null;
let selectedClassrooms = [];  // Array to hold multiple selected classrooms

// Add event listeners for time slot selection
const timeSlotOptions = document.querySelectorAll("#time-slot-options a");
timeSlotOptions.forEach(option => {
    option.addEventListener("click", function(event) {
        event.preventDefault();
        selectedTimeSlot = event.target.innerText;
        document.getElementById('time-slot-btn').innerText = selectedTimeSlot; // Update the text shown on that dropdown button
    });
});

// Event listeners for selecting multiple classrooms
const classroomButtons = document.querySelectorAll("#classroom-buttons button");
classroomButtons.forEach(button => {
    button.addEventListener("click", function() {
        const classroom = button.innerText;
        const currentBgColor = window.getComputedStyle(button).backgroundColor;

        if (currentBgColor === "rgba(255, 255, 255, 0.2)") {
            button.style.backgroundColor = "rgba(255, 255, 255, 0.9)";
            if (!selectedClassrooms.includes(classroom)) {
                selectedClassrooms.push(classroom);  // Add classroom to the array
            }
        } else {
            button.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
            selectedClassrooms = selectedClassrooms.filter(c => c !== classroom);  // Remove classroom from the array
        }
    });
});

// SEE BOOKINGS ON WEBPAGE WITH DYNAMIC WIDGETS //


// Function to fetch bookings and create dynamic frosted-glass tiles outside the container
function see_bookings() {
    fetch('http://127.0.0.1:8000/see_bookings') // Assuming API is already set up to return bookings
        .then(response => response.json())
        .then(data => {
            // Create a new div outside the 'container' to hold the tiles
            let externalContainer = document.getElementById('external-bookings-container');
            
            if (!externalContainer) {
                externalContainer = document.createElement('div');
                externalContainer.id = 'external-bookings-container';
                //externalContainer.classList.add(externalContainerStyle);
                document.body.appendChild(externalContainer); // Append outside the container
            }

            externalContainer.innerHTML = '';  // Clear any previous content
            const bookingTitle = document.createElement('h1');
            bookingTitle.innerHTML = 'Bookings';
            externalContainer.appendChild(bookingTitle)

            // Loop through the bookings data and create frosted-glass tiles
            data.forEach(booking => {

                const bookingTile = document.createElement('div');
                bookingTile.classList.add('booking-tile');

                // Add classroom name in larger font
                const classroomName = document.createElement('h2');
                classroomName.innerText = booking.classroom;
                bookingTile.appendChild(classroomName);

                // Add time slot in smaller font
                const timeSlot = document.createElement('p');
                timeSlot.innerText = `Time Slot: ${booking.time_slot}`;
                timeSlot.classList.add('small-text');
                bookingTile.appendChild(timeSlot);

                // Add purpose in even smaller font
                const purpose = document.createElement('p');
                purpose.innerText = `Purpose: ${booking.purpose}`;
                purpose.classList.add('tiny-text');
                bookingTile.appendChild(purpose);

                externalContainer.appendChild(bookingTile); // Append each tile to the new container
            });
        })
        .catch(error => console.error('Error fetching bookings:', error));
}

// Add the event listener to the 'See Bookings' button
document.getElementById('see_bookings_button_id').addEventListener('click', see_bookings);

// CSS for frosted-glass tiles and styling (displayed outside the parent container)
const styleElement = document.createElement('style');
styleElement.innerHTML = `
        #external-bookings-container {
        position: absolute;
        left: 50%;
        top: 0;
        transform: translateX(-50%);
        width: 600px; /* Adjusted width for grid layout */
        height: 100vh; /* Full viewport height */
        padding: 10px;
        background: rgba(255, 255, 255, 0.5); /* Slightly darker background for visibility */
        overflow-y: auto; /* Scroll if content overflows */
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); /* Define columns for square-like layout */
        grid-auto-rows: minmax(150px, auto); /* Set row height to make squares */
        gap: 10px;
        align-content: start; /* Align grid items at the start of the container */
    }

    .booking-tile {
        width: 150px; /* Smaller size */
        padding: 10px;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: left;
    }

    .booking-tile h2 {
        font-size: 1.2em;
        margin-bottom: 8px;
    }

    .booking-tile .small-text {
        font-size: 1em;
        color: white;
    }

    .booking-tile .tiny-text {
        font-size: 0.9em;
        color: white;
    }
`;
document.head.appendChild(styleElement);






// Function that sends booking data to the API
function sendBookingData() {                                          
    const purpose = document.getElementById("purpose").value;
    
    // Create a data object to send to the API
    const bookingData = {
        time_slot: selectedTimeSlot,   // Time slot selected from the dropdown list
        classrooms: selectedClassrooms,  // Array of selected classrooms
        purpose: purpose    // Purpose for booking
    };

    // Send booking data to the Python API using Fetch
    fetch('http://127.0.0.1:8000/book', {   // API endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())   // Handle JSON response
    .then(data => {
        console.log(data.message);  // Output message from Flask
    })                       
    .catch(error => {
        console.error('Error:', error);   // Handle any errors
    });
}

// Add event listener for the "Book" button
const bookButton = document.getElementById("book-btn");
bookButton.addEventListener("click", function() {
    const purpose = document.getElementById("purpose").value;

    console.log("Booking Details:");
    console.log("Time Slot:", selectedTimeSlot ? selectedTimeSlot : "No time slot selected");   
    console.log("Classrooms:", selectedClassrooms.length > 0 ? selectedClassrooms.join(', ') : "No classrooms selected");
    console.log("Purpose:", purpose ? purpose : "You have no purpose");               

    // Call the function to send data to the Python API
    sendBookingData();
});

 ///////////// UPDATE CLASSROOM BUTTONS BASED ON TIMESLOT SELECTED //////////////



//const timeSlotOptions = document.querySelectorAll("#time-slot-options a");
timeSlotOptions.forEach(option => {
    option.addEventListener("click", function(event) {
        event.preventDefault();
        selectedTimeSlot = event.target.innerText;
        document.getElementById('time-slot-btn').innerText = selectedTimeSlot;
        
        // Fetch available classrooms for the selected time slot
        fetchAvailableClassrooms(selectedTimeSlot);
    });
});




// Function to fetch available classrooms from the API
function fetchAvailableClassrooms(timeSlot) {
    fetch(`http://127.0.0.1:8000/available_classrooms/${timeSlot}`)
        .then(response => {
            console.log('fetchAvailableClassrooms fetched.');
            return response.json();
        })
        .then(data => {
            const availableClassrooms = data.available_classrooms;
            console.log('Available Classrooms:', availableClassrooms);  // Log the actual data
            updateClassroomButtons(availableClassrooms);  // Update the buttons
        })
        .catch(error => console.error('Error:', error));
}

// Function to update classroom buttons based on availability
function updateClassroomButtons(availableClassrooms) {
    const classroomButtons = document.querySelectorAll("#classroom-buttons button");
    console.log('updateClassroomButtons called.');
    classroomButtons.forEach(button => {
        const classroom = button.innerText.trim();  // Trim any extra spaces

        if (availableClassrooms.includes(classroom)) {
            button.style.display = "inline-block";  // Show available classrooms
        } else {
            button.style.display = "none";  // Hide unavailable classrooms
        }
    });
}

// NAVIGATION FUNCTIONS

const loginButtonObject = document.getElementById('login_button_id');
const bookingButtonObject = document.getElementById('booking_button_id');
const finalizeButtonObject = document.getElementById('finalize_button_id');

loginButtonObject.addEventListener('click', function(){

    console.log('login clicked')

    document.getElementById('booking_tab_id').style.visibility = 'hidden';
    document.getElementById('finalize_tab_id').style.visibility = 'hidden';
    document.getElementById('login_tab_id').style.visibility = 'visible';

});

bookingButtonObject.addEventListener('click', function(){

    console.log('book clicked')

    document.getElementById('booking_tab_id').style.visibility = 'visible';
    document.getElementById('finalize_tab_id').style.visibility = 'hidden';
    document.getElementById('login_tab_id').style.visibility = 'hidden';

});

finalizeButtonObject.addEventListener('click', function(){

    console.log('finalize clicked')

    document.getElementById('booking_tab_id').style.visibility = 'hidden';
    document.getElementById('finalize_tab_id').style.visibility = 'visible';
    document.getElementById('login_tab_id').style.visibility = 'hidden';

});
