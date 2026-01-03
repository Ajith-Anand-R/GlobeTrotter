document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '../login_/_signup_screen/code.html';
        return;
    }

    const tripGrid = document.querySelector('.grid');
    const countText = document.querySelector('p.text-gray-400');
    const newTripBtn = document.querySelector('button.bg-primary');

    if (newTripBtn) {
        newTripBtn.addEventListener('click', () => {
            window.location.href = '../create_trip_screen/code.html';
        });
    }

    async function fetchTrips() {
        try {
            const response = await fetch('http://127.0.0.1:8000/trips/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const trips = await response.json();
                renderTrips(trips);
            }
        } catch (err) {
            console.error('Failed to fetch trips', err);
        }
    }

    function renderTrips(trips) {
        if (countText) {
            countText.textContent = `Manage your upcoming journeys and relive past memories. You have ${trips.filter(t => t.status === 'upcoming').length} upcoming trips.`;
        }

        if (trips.length === 0) {
            tripGrid.innerHTML = '<div class="col-span-full text-center py-20 bg-white/5 rounded-3xl border border-dashed border-white/20"><span class="material-symbols-outlined text-6xl text-white/10 mb-4">explore</span><p class="text-white/40">No trips found. Create your first adventure!</p></div>';
            return;
        }

        tripGrid.innerHTML = trips.map(trip => `
            <div class="group relative aspect-[4/5] sm:aspect-[4/3] md:aspect-[3/4] overflow-hidden rounded-2xl border border-white/10 hover:border-primary/50 transition-all duration-500 hover:shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)]">
                <div class="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-110" style='background-image: url("${trip.cover_image_url || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&q=80&w=800'}");'></div>
                <div class="absolute inset-0 glass-card-overlay opacity-80 group-hover:opacity-60 transition-opacity"></div>
                
                <!-- Status Badge -->
                <div class="absolute top-4 left-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${trip.status === 'upcoming' ? 'bg-primary' : 'bg-white/5'} text-white border border-white/20 shadow-lg backdrop-blur-md">
                        ${trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
                    </span>
                </div>

                <!-- Action Menu (Visible on Hover) -->
                <div class="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
                    <button onclick="event.stopPropagation(); window.location.href='../itinerary_builder_screen/code.html?tripId=${trip.id}'" class="p-2 rounded-full bg-black/40 hover:bg-primary text-white backdrop-blur-sm shadow-lg" title="View Itinerary">
                        <span class="material-symbols-outlined text-[20px]">visibility</span>
                    </button>
                    <button onclick="event.stopPropagation(); window.location.href='../create_trip_screen/code.html?tripId=${trip.id}'" class="p-2 rounded-full bg-black/40 hover:bg-blue-500 text-white backdrop-blur-sm shadow-lg" title="Edit Trip">
                        <span class="material-symbols-outlined text-[20px]">edit</span>
                    </button>
                    <button onclick="event.stopPropagation(); deleteTrip(${trip.id})" class="p-2 rounded-full bg-black/40 hover:bg-red-500 text-white backdrop-blur-sm shadow-lg" title="Delete Trip">
                        <span class="material-symbols-outlined text-[20px]">delete</span>
                    </button>
                </div>

                <!-- Card Content -->
                <div onclick="window.location.href='../itinerary_builder_screen/code.html?tripId=${trip.id}'" class="cursor-pointer absolute bottom-0 inset-x-0 p-5 bg-white/5 backdrop-blur-xl border-t border-white/10 flex flex-col gap-2 translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
                    <h3 class="text-xl font-bold text-white leading-tight">${trip.title}</h3>
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-2 text-primary-light text-sm font-medium">
                            <span class="material-symbols-outlined text-[16px]">calendar_today</span>
                            <span>${new Date(trip.start_date).toLocaleDateString()} - ${new Date(trip.end_date).toLocaleDateString()}</span>
                        </div>
                        <div class="flex items-center justify-between mt-2">
                            <span class="text-xs text-gray-300 font-medium">${trip.stops?.length || 0} Destinations</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    window.deleteTrip = async (id) => {
        if (!confirm('Are you sure you want to delete this trip?')) return;
        try {
            const response = await fetch(`http://127.0.0.1:8000/trips/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) fetchTrips();
        } catch (err) {
            alert('Failed to delete trip');
        }
    };

    fetchTrips();
});
