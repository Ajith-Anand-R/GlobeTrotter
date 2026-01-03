document.addEventListener('DOMContentLoaded', async () => {
    const createTripBtn = document.querySelector('button.bg-primary');
    const tripNameInput = document.querySelector('input[placeholder="e.g., Summer in Kyoto"]');
    const startDateInput = document.querySelector('input[type="date"]:first-of-type');
    const endDateInput = document.querySelectorAll('input[type="date"]')[1];
    const descriptionInput = document.querySelector('textarea');
    const uploadDiv = document.querySelector('.border-dashed'); // Cover photo upload area
    const titleHeader = document.querySelector('h1.text-3xl');

    let coverImageUrl = "";
    const urlParams = new URLSearchParams(window.location.search);
    const tripId = urlParams.get('tripId');

    // Function to set background
    const setCoverImage = (url) => {
        coverImageUrl = url;
        uploadDiv.style.backgroundImage = `url('${url}')`;
        uploadDiv.style.backgroundSize = 'cover';
        uploadDiv.style.backgroundPosition = 'center';
        const innerText = uploadDiv.querySelector('.relative.z-10');
        if (innerText) innerText.style.display = 'none';
    };

    if (uploadDiv) {
        uploadDiv.addEventListener('click', () => {
            const url = prompt("Enter a cover image URL (optional):", coverImageUrl || "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&q=80&w=800");
            if (url) {
                setCoverImage(url);
            }
        });
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('You must be logged in.');
        window.location.href = '../login_/_signup_screen/code.html';
        return;
    }

    // If editing, load data
    if (tripId) {
        if (titleHeader) titleHeader.textContent = "Loading Trip Details...";
        if (createTripBtn) createTripBtn.textContent = "Updating...";

        console.log(`Fetching trip data for tripId: ${tripId}`);
        try {
            const response = await fetch(`http://127.0.0.1:8000/trips/${tripId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const trip = await response.json();
                if (titleHeader) titleHeader.textContent = "Edit Your Adventure";
                if (createTripBtn) createTripBtn.textContent = "Update Trip";
                console.log('Trip data received:', trip);

                // Helper to format date for <input type="date">
                const formatDateForInput = (dateStr) => {
                    if (!dateStr) return "";
                    // Handle space or T separator
                    const datePart = dateStr.includes('T') ? dateStr.split('T')[0] : dateStr.split(' ')[0];
                    return datePart;
                };

                if (tripNameInput) tripNameInput.value = trip.title || "";
                if (startDateInput) startDateInput.value = formatDateForInput(trip.start_date);
                if (endDateInput) endDateInput.value = formatDateForInput(trip.end_date);
                if (descriptionInput) descriptionInput.value = trip.description || "";

                if (trip.cover_image_url) {
                    setCoverImage(trip.cover_image_url);
                }
            } else {
                if (response.status === 401) {
                    alert('Session expired. Please log in again.');
                    window.location.href = '../login_/_signup_screen/code.html';
                } else {
                    const errData = await response.json();
                    console.error('Failed to load trip:', errData);
                    alert(`Failed to load trip data: ${errData.detail || 'Unknown error'}`);
                }
            }
        } catch (err) {
            console.error('Error loading trip:', err);
            alert('Error connecting to backend. Please ensure the server is running.');
        }
    }

    if (!createTripBtn) return;

    createTripBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        const tripData = {
            title: tripNameInput.value,
            destination: tripNameInput.value,
            description: descriptionInput.value,
            start_date: startDateInput.value,
            end_date: endDateInput.value,
            completion_percentage: 0,
            cost_from: 0,
            cover_image_url: coverImageUrl,
            status: "upcoming"
        };

        if (!tripData.title || !tripData.start_date || !tripData.end_date) {
            alert('Please fill in Name, Start Date, and End Date.');
            return;
        }

        const url = tripId ? `http://127.0.0.1:8000/trips/${tripId}` : 'http://127.0.0.1:8000/trips/';
        const method = tripId ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(tripData)
            });

            if (response.ok) {
                alert(`Trip ${tripId ? 'updated' : 'created'} successfully!`);
                window.location.href = '../my_trips_screen/code.html';
            } else {
                if (response.status === 401) {
                    alert('Session expired. Please log in again.');
                    window.location.href = '../login_/_signup_screen/code.html';
                } else {
                    const error = await response.json();
                    alert(error.detail || `Failed to ${tripId ? 'update' : 'create'} trip`);
                }
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred. Make sure the backend is running.');
        }
    });
});
