document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    const urlParams = new URLSearchParams(window.location.search);
    const tripId = urlParams.get('tripId');

    if (!token) {
        window.location.href = '../login_/_signup_screen/code.html';
        return;
    }

    if (!tripId) {
        alert('No trip selected');
        window.location.href = '../my_trips_screen/code.html';
        return;
    }

    const tripTitleHeader = document.querySelector('h1.text-xl');
    const tripDatesSub = document.querySelector('div.text-xs.text-gray-400 span:first-child');
    const stopCardsContainer = document.querySelector('section.flex-1.overflow-y-auto .max-w-4xl');
    const saveBtn = document.querySelector('button.bg-primary');

    // Set Budget Link
    const budgetBtn = document.getElementById('btnTripBudget');
    if (budgetBtn) budgetBtn.href = `../expenses_screen/code.html?tripId=${tripId}`;

    // View Mode Toggle
    let isEditMode = false;
    const toggleBtn = document.createElement('button');
    toggleBtn.className = "flex items-center gap-2 px-4 py-2 ml-4 bg-gray-700 hover:bg-gray-600 text-white text-sm font-bold rounded-lg transition-all";
    toggleBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">edit</span><span>Edit Mode</span>';
    if (saveBtn) saveBtn.parentNode.insertBefore(toggleBtn, saveBtn);

    toggleBtn.addEventListener('click', () => {
        isEditMode = !isEditMode;
        toggleBtn.innerHTML = isEditMode
            ? '<span class="material-symbols-outlined text-[18px]">visibility</span><span>View Mode</span>'
            : '<span class="material-symbols-outlined text-[18px]">edit</span><span>Edit Mode</span>';
        toggleBtn.classList.toggle('bg-primary', isEditMode);
        document.body.classList.toggle('editing', isEditMode);
        fetchTripDetails(); // Re-render to show/hide controls
    });

    // API Helpers
    const api = async (endpoint, method, body) => {
        try {
            const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
                method,
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: body ? JSON.stringify(body) : undefined
            });
            if (!res.ok) throw await res.json();
            return await res.json();
        } catch (e) {
            alert(e.detail || "API Error");
            console.error(e);
        }
    };

    async function fetchTripDetails() {
        const trip = await api(`/trips/${tripId}`, 'GET');
        if (trip) renderTrip(trip);
    }

    function renderTrip(trip) {
        if (tripTitleHeader) tripTitleHeader.textContent = trip.title;
        if (tripDatesSub) {
            const start = new Date(trip.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const end = new Date(trip.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            tripDatesSub.textContent = `${start} - ${end}`;
        }

        if (stopCardsContainer) {
            const stops = (trip.stops || []).sort((a, b) => a.sort_order - b.sort_order);

            const stopsHtml = stops.map(stop => `
                <div class="glass-card rounded-2xl p-0 overflow-hidden group mb-8 relative stop-card" draggable="${isEditMode}" data-id="${stop.id}">
                    <div class="h-32 w-full bg-cover bg-center relative" style="background-image: url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&q=80&w=800');">
                        <div class="absolute inset-0 bg-gradient-to-t from-[#1b171a] via-transparent to-transparent opacity-90"></div>
                        <div class="absolute bottom-4 left-6">
                            <h2 class="text-3xl font-bold text-white shadow-black drop-shadow-md">${stop.city_name}</h2>
                        </div>
                        ${isEditMode ? `
                        <div class="absolute top-4 right-4 flex gap-2">
                             <button onclick="editStop(${stop.id}, '${stop.city_name}', '${stop.arrival_date}', '${stop.departure_date}', ${stop.sort_order})" class="size-8 rounded-full bg-black/40 backdrop-blur-md flex items-center justify-center text-white hover:bg-primary transition-colors"><span class="material-symbols-outlined text-sm">edit</span></button>
                             <button onclick="deleteStop(${stop.id})" class="size-8 rounded-full bg-black/40 backdrop-blur-md flex items-center justify-center text-white hover:bg-red-500 transition-colors"><span class="material-symbols-outlined text-sm">delete</span></button>
                        </div>
                        <div class="absolute top-1/2 left-2 -translate-y-1/2 text-white/30 hover:text-white cursor-grab active:cursor-grabbing p-2 grab-handle">
                            <span class="material-symbols-outlined">drag_indicator</span>
                        </div>
                        ` : ''}
                    </div>
                    <div class="p-6">
                        <div class="flex flex-wrap gap-4 mb-6">
                            <div class="flex items-center gap-2 bg-white/5 px-3 py-2 rounded-lg border border-white/10">
                                <span class="material-symbols-outlined text-gray-400">calendar_today</span>
                                <span class="text-sm font-medium">${new Date(stop.arrival_date).toLocaleDateString()} - ${new Date(stop.departure_date).toLocaleDateString()}</span>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Activities</h4>
                            ${(stop.activities || []).map(act => `
                                <div class="flex items-center gap-4 p-3 rounded-xl bg-white/5 border border-white/5 group/activity">
                                    <div class="flex-1 min-w-0">
                                        <p class="font-medium text-white truncate">${act.description}</p>
                                        <p class="text-xs text-gray-400 truncate">${act.time || 'All Day'} • $${act.cost || 0}</p>
                                    </div>
                                    ${isEditMode ? `
                                    <div class="flex gap-2 opacity-100 transition-opacity">
                                        <button onclick="editActivity(${act.id}, '${act.description}', '${act.time}', ${act.cost})" class="text-gray-400 hover:text-white"><span class="material-symbols-outlined text-lg">edit</span></button>
                                        <button onclick="deleteActivity(${act.id})" class="text-gray-400 hover:text-red-400"><span class="material-symbols-outlined text-lg">close</span></button>
                                    </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                            ${isEditMode ? `
                            <button onclick="addActivityPrompt(${stop.id})" class="w-full py-2 flex items-center justify-center gap-2 rounded-lg border border-dashed border-gray-600 text-gray-400 hover:text-primary hover:border-primary hover:bg-primary/5 transition-all mt-2">
                                <span class="material-symbols-outlined text-sm">add</span>
                                <span class="text-sm font-medium">Add Activity</span>
                            </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('');

            stopCardsContainer.innerHTML = `
                <div class="flex flex-col" id="stops-list">
                    ${stopsHtml}
                    ${isEditMode ? `
                    <button id="addStopBtn" class="w-full h-24 rounded-2xl border-2 border-dashed border-gray-700 hover:border-primary hover:bg-primary/5 transition-all flex flex-col items-center justify-center group cursor-pointer mt-4">
                        <div class="size-10 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary group-hover:scale-110 transition-all duration-300">
                            <span class="material-symbols-outlined text-primary group-hover:text-white">add_location_alt</span>
                        </div>
                        <span class="text-sm font-medium text-gray-400 mt-2 group-hover:text-primary-light">Add Next Destination</span>
                    </button>
                    ` : ''}
                </div>
            `;

            if (isEditMode) {
                document.getElementById('addStopBtn')?.addEventListener('click', addStopPrompt);
                setupDragAndDrop();
            }
        }
    }

    // Drag and Drop Logic
    function setupDragAndDrop() {
        const list = document.getElementById('stops-list');
        let draggedItem = null;

        list.querySelectorAll('.stop-card').forEach(item => {
            item.addEventListener('dragstart', e => {
                draggedItem = item;
                e.dataTransfer.effectAllowed = 'move';
                setTimeout(() => item.style.opacity = '0.5', 0);
            });

            item.addEventListener('dragend', async () => {
                draggedItem.style.opacity = '1';
                draggedItem = null;

                // Save new order
                const newOrderIds = Array.from(list.querySelectorAll('.stop-card')).map(el => parseInt(el.dataset.id));
                await api(`/trips/${tripId}/reorder_stops`, 'POST', { stop_ids: newOrderIds });
            });

            item.addEventListener('dragover', e => {
                e.preventDefault();
                const afterElement = getDragAfterElement(list, e.clientY);
                if (afterElement == null) {
                    list.insertBefore(draggedItem, list.querySelector('#addStopBtn'));
                } else {
                    list.insertBefore(draggedItem, afterElement);
                }
            });
        });
    }

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.stop-card:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // --- SEARCH LOGIC ---
    let searchType = 'city'; // 'city' or 'activity'
    let currentStopId = null;
    let currentCityName = null; // Store city name for activity search
    let currentTrip = null; // Store trip globally
    let searchDebounce;

    // Extend fetchTripDetails to store currentTrip
    const originalFetchTripDetails = fetchTripDetails;
    fetchTripDetails = async () => {
        currentTrip = await api(`/trips/${tripId}`, 'GET');
        if (currentTrip) renderTrip(currentTrip);
    };

    window.openSearchModal = (type, stopId = null, cityName = null) => {
        searchType = type;
        currentStopId = stopId;
        currentCityName = cityName;

        const modal = document.getElementById('searchModal');
        const input = document.getElementById('searchInput');
        const results = document.getElementById('searchResults');

        modal.classList.remove('hidden');
        input.value = '';
        input.placeholder = type === 'city' ? "Search cities (e.g., Paris)..." : `Search activities in ${cityName || 'city'}...`;
        input.focus();
        results.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-gray-500 min-h-[200px]">
                <span class="material-symbols-outlined text-4xl mb-2 opacity-50">${type === 'city' ? 'location_city' : 'local_activity'}</span>
                <p>${type === 'city' ? 'Where to next?' : `Looking for fun in ${cityName || 'town'}?`}</p>
                ${type === 'activity' ? '<p class="text-xs mt-2">Try "Museum", "Food", or "Tour"</p>' : ''}
            </div>
        `;

        input.onkeyup = (e) => {
            clearTimeout(searchDebounce);
            searchDebounce = setTimeout(() => performSearch(e.target.value), 300);
        };

        // Auto-search for activities if city is known
        if (type === 'activity' && cityName) {
            performSearch('');
        }
    };

    window.closeSearchModal = () => {
        document.getElementById('searchModal').classList.add('hidden');
    };

    async function performSearch(query) {
        const resultsContainer = document.getElementById('searchResults');
        resultsContainer.innerHTML = '<div class="text-center text-gray-500 py-8">Searching...</div>';

        try {
            let items = [];
            if (searchType === 'city') {
                items = await api(`/cities/search?query=${encodeURIComponent(query)}`, 'GET');
                renderCityResults(items);
            } else {
                // Activity Search
                // 1. Get City ID
                let cityId = null;
                if (currentCityName) {
                    const cities = await api(`/cities/search?query=${encodeURIComponent(currentCityName)}`, 'GET');
                    // Find exact match or first
                    const city = cities.find(c => c.name.toLowerCase() === currentCityName.toLowerCase()) || cities[0];
                    if (city) cityId = city.id;
                }

                if (!cityId) {
                    resultsContainer.innerHTML = '<div class="text-center text-yellow-400 py-8">City not found in catalog. Add custom activity?</div>';
                    // Fallback to custom add logic UI?
                    return;
                }

                // 2. Search Activities
                items = await api(`/activities/search?city_id=${cityId}&query=${encodeURIComponent(query)}`, 'GET');
                renderActivityResults(items);
            }
        } catch (e) {
            console.error(e);
            resultsContainer.innerHTML = '<div class="text-center text-red-400 py-8">Search failed.</div>';
        }
    }

    function renderCityResults(cities) {
        const container = document.getElementById('searchResults');
        if (!cities || cities.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 py-8">No cities found.</div>';
            return;
        }

        container.innerHTML = cities.map(city => `
            <div class="glass-card p-4 rounded-xl flex gap-4 items-center group hover:bg-white/5 transition-colors">
                <div class="size-16 rounded-lg bg-cover bg-center shrink-0" style="background-image: url('${city.image_url || 'https://via.placeholder.com/150'}')"></div>
                <div class="flex-1">
                    <h3 class="font-bold text-white text-lg">${city.name}</h3>
                    <p class="text-xs text-gray-400">${city.country} • Cost Index: ${city.cost_index} • Pop: ${city.popularity}</p>
                    <p class="text-xs text-gray-500 mt-1 line-clamp-1">${city.description}</p>
                </div>
                <button onclick="selectCityForStop('${city.name}')" class="px-4 py-2 bg-primary/20 text-primary-light hover:bg-primary hover:text-white rounded-lg text-sm font-bold transition-all">
                    Add
                </button>
            </div>
        `).join('');
    }

    function renderActivityResults(activities) {
        const container = document.getElementById('searchResults');
        if (!activities || activities.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-500 py-8 flex flex-col items-center">
                    <p>No catalog activities found.</p>
                    <button onclick="addCustomActivity()" class="mt-4 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 text-sm">Add Custom Activity</button>
                </div>`;
            return;
        }

        container.innerHTML = activities.map(act => `
            <div class="glass-card p-4 rounded-xl flex gap-4 items-center group hover:bg-white/5 transition-colors">
                 <div class="size-16 rounded-lg bg-cover bg-center shrink-0" style="background-image: url('${act.image_url || 'https://via.placeholder.com/150'}')"></div>
                <div class="flex-1">
                    <h3 class="font-bold text-white text-lg">${act.name}</h3>
                    <p class="text-xs text-gray-400">${act.category} • ${act.duration} • $${act.cost}</p>
                    <p class="text-xs text-gray-500 mt-1 line-clamp-1">${act.description}</p>
                </div>
                <button onclick="selectActivity('${act.name}', '${act.duration}', ${act.cost})" class="px-4 py-2 bg-primary/20 text-primary-light hover:bg-primary hover:text-white rounded-lg text-sm font-bold transition-all">
                    Add
                </button>
            </div>
        `).join('');
        // Add custom button at bottom
        container.innerHTML += `
             <div class="text-center pt-4 border-t border-white/5 mt-4">
                <button onclick="addCustomActivity()" class="text-xs text-gray-500 hover:text-white underline">Can't find it? Add custom activity</button>
            </div>
        `;
    }

    window.selectCityForStop = async (cityName) => {
        closeSearchModal();
        // Proceed with original add flow, pre-filled
        const arrival = prompt(`Arrival in ${cityName} (YYYY-MM-DD):`, new Date().toISOString().split('T')[0]);
        if (!arrival) return;
        const departure = prompt(`Departure from ${cityName} (YYYY-MM-DD):`, new Date().toISOString().split('T')[0]);

        await api(`/trips/${tripId}/stops`, 'POST', { city_name: cityName, arrival_date: arrival, departure_date: departure, sort_order: 99 });
        fetchTripDetails();
    };

    window.selectActivity = async (desc, time, cost) => {
        closeSearchModal();
        await api(`/stops/${currentStopId}/activities`, 'POST', { description: desc, time: time, cost: cost });
        fetchTripDetails();
    }

    window.addCustomActivity = async () => {
        closeSearchModal();
        const desc = prompt("Activity Description:");
        if (!desc) return;
        const time = prompt("Time (e.g., 2 hours or 10:00 AM):", "2 hours");
        const cost = parseFloat(prompt("Cost ($):", "0"));
        await api(`/stops/${currentStopId}/activities`, 'POST', { description: desc, time, cost });
        fetchTripDetails();
    }

    // Override original global handlers
    window.addStopPrompt = () => {
        openSearchModal('city');
    };

    window.addActivityPrompt = (stopId) => {
        const stop = currentTrip.stops.find(s => s.id === stopId);
        openSearchModal('activity', stopId, stop ? stop.city_name : null);
    };

    // Global Action Handlers
    window.editStop = async (id, city, arr, dep, order) => {
        const newCity = prompt("Edit City Name:", city);
        if (!newCity) return;
        const newArr = prompt("Edit Arrival:", arr.split('T')[0]);
        const newDep = prompt("Edit Departure:", dep.split('T')[0]);

        await api(`/stops/${id}`, 'PUT', { city_name: newCity, arrival_date: newArr, departure_date: newDep, sort_order: order });
        fetchTripDetails();
    };

    window.deleteStop = async (id) => {
        if (confirm("Delete this stop?")) {
            await api(`/stops/${id}`, 'DELETE');
            fetchTripDetails();
        }
    };

    // Removed old addActivityPrompt as it's now handled by window.addActivityPrompt above

    window.editActivity = async (id, desc, time, cost) => {
        const newDesc = prompt("Edit Description:", desc);
        if (!newDesc) return;
        const newTime = prompt("Edit Time:", time);
        const newCost = parseFloat(prompt("Edit Cost:", cost));

        await api(`/activities/${id}`, 'PUT', { description: newDesc, time: newTime, cost: newCost });
        fetchTripDetails();
    };

    window.deleteActivity = async (id) => {
        if (confirm("Delete this activity?")) {
            await api(`/activities/${id}`, 'DELETE');
            fetchTripDetails();
        }
    };

    fetchTripDetails();
});
