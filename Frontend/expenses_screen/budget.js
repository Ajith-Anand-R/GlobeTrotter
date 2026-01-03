document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    const urlParams = new URLSearchParams(window.location.search);
    const tripId = urlParams.get('tripId');

    if (!token) {
        window.location.href = '../login_/_signup_screen/code.html';
        return;
    }

    if (!tripId) {
        alert("No trip specified.");
        // window.location.href = '../my_trips_screen/code.html';
        return;
    }

    const api = async (endpoint) => {
        try {
            const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw await res.json();
            return await res.json();
        } catch (e) {
            console.error(e);
            alert("Failed to load budget data");
        }
    };

    async function loadBudget() {
        const data = await api(`/trips/${tripId}/budget`);
        if (!data) return;

        // Update Text Values
        document.getElementById('totalCostDisplay').textContent = `$${data.total_cost.toLocaleString()}`;
        document.getElementById('dailyAvgVal').textContent = Math.round(data.daily_average).toLocaleString();
        document.getElementById('budgetLimitVal').textContent = data.budget_limit.toLocaleString();

        // Category Cards
        document.getElementById('catStayCost').textContent = data.breakdown.accommodation.toLocaleString();
        document.getElementById('catTransCost').textContent = data.breakdown.transport.toLocaleString();
        document.getElementById('catActCost').textContent = data.breakdown.activities.toLocaleString();
        document.getElementById('catMealsCost').textContent = data.breakdown.meals.toLocaleString();

        // Progress Bar
        const limit = data.budget_limit || 1; // Avoid divide by zero
        const percent = Math.min((data.total_cost / limit) * 100, 100);
        const progressBar = document.getElementById('budgetProgressBar');
        progressBar.style.width = `${percent}%`;

        const statusText = document.getElementById('budgetStatusText');
        statusText.textContent = `${Math.round(percent)}% of budget used`;

        if (data.total_cost > data.budget_limit && data.budget_limit > 0) {
            progressBar.classList.remove('bg-primary');
            progressBar.classList.add('bg-red-500');
            statusText.classList.add('text-red-400');
            statusText.textContent = `Over budget by $${(data.total_cost - data.budget_limit).toLocaleString()}`;
        }

        // Render Chart
        renderChart(data.breakdown);
    }

    function renderChart(breakdown) {
        const ctx = document.getElementById('budgetChart').getContext('2d');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Accommodation', 'Transport', 'Activities', 'Meals'],
                datasets: [{
                    data: [breakdown.accommodation, breakdown.transport, breakdown.activities, breakdown.meals],
                    backgroundColor: [
                        '#3B82F6', // Blue for Stay
                        '#10B981', // Green for Transport
                        '#A855F7', // Purple for Activities
                        '#F97316'  // Orange for Meals
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#9CA3AF',
                            font: { family: 'Urbanist', size: 14 },
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    loadBudget();
});
