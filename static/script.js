function createUser(event) {
    event.preventDefault();

    const xhttp = new XMLHttpRequest();
    const username = document.getElementById("usernameBox").value;
    const password = document.getElementById("passwordBox").value;
    const body = {"username": username, "password": password};
    xhttp.open("POST", "/register", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(body));
    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        console.log(data);

        if (this.status === 201) {
            document.getElementById("signupForm").reset();
            window.location.href = "/login";
        }
    }
}

function handleLogin(event) {
    event.preventDefault();

    const xhttp = new XMLHttpRequest();
    const username = document.getElementById("usernameBox").value;
    const password = document.getElementById("passwordBox").value;
    const body = {"username": username, "password": password};
    xhttp.open("POST", "/login", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(body));
    xhttp.onload = function() {
        //const data = JSON.parse(this.responseText);
        //console.log(data);
        console.log("Raw response:", this.responseText);  // add this

        console.log("Status: ", this.status);
        //console.log("Responsse: ", this.data);


        if (this.status === 200) {
            window.location.href = "/";
        } else {
            alert(this.responseText);
        }
    }

    
}

document.addEventListener('DOMContentLoaded', function () {
    const monthYearEl = document.getElementById('month-year');
    const daysEl = document.getElementById('days');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const todayBtn = document.getElementById('today-btn');
    const eventDateEl = document.getElementById('event-date');
    const eventListEl = document.getElementById('event-list');

    let currentDate = new Date();
    let selectedDate = null;

    // Sample events data with multiple colors
    const events = {
        '2026-5-1': [{ time: '5:30 PM', text: 'Club Meeting', color: "gg-red" }],
        '2026-5-8': [{ time: '5:30 PM', text: 'Club Meeting', color: "casual-yellow" }],
        '2026-5-13': [
            { time: '4:00 PM', text: 'Tekken 8 Tournament', color: "tournament" },
          
        ],
        '2026-5-15': [{ time: '5:30 PM', text: 'Club Meeting', color: "gg-red" }],
        '2026-5-22': [{ time: '5:30 PM', text: 'Club Meeting', color: "gg-red" }],
        '2026-5-29': [{ time: '5:30 PM', text: 'Club Meeting', color: "gg-red" }]
    };

    function renderCalendar() {
    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    const prevLastDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0);

    const firstDayIndex = firstDay.getDay();
    const lastDayIndex = lastDay.getDay();
    const nextDays = 7 - lastDayIndex - 1;

    const months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    monthYearEl.innerHTML = `${months[currentDate.getMonth()]} ${currentDate.getFullYear()}`;

    let daysHtml = "";

    // 1. Previous month days (empty slots)
    for (let x = firstDayIndex; x > 0; x--) {
        const prevDate = prevLastDay.getDate() - x + 1;
        daysHtml += `<div class="day other-month">${prevDate}</div>`;
    }

    // 2. Current month days
    for (let i = 1; i <= lastDay.getDate(); i++) {
        const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
        const dateKey = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${i}`;
        const dayEvents = events[dateKey] || []; // Get events for this day

        let dayClass = 'day';

        // Check if day is today
        if (date.toDateString() === new Date().toDateString()) {
            dayClass += ' today';
        }

        // Check if day is selected
        if (selectedDate && date.toDateString() === selectedDate.toDateString()) {
            dayClass += ' selected';
        }

        // Check if day has any events at all
        if (dayEvents.length > 0) {
            dayClass += ' has-events';
        }

        // --- THE DOT LOGIC ---
        // Create the container and loop through each event to add its specific color dot
        let dotsHtml = '<div class="event-dots-container">';
        dayEvents.forEach(e => {
            // This applies 'tournament', 'gg-red', etc., to the dots on the left
            dotsHtml += `<div class="dot ${e.color || ''}"></div>`;
        });
        dotsHtml += '</div>';

        daysHtml += `<div class="${dayClass}" data-date="${dateKey}">
                        ${i}
                        ${dotsHtml}
                     </div>`;
    }

    // 3. Next month days (empty slots)
    for (let j = 1; j <= nextDays; j++) {
        daysHtml += `<div class="day other-month">${j}</div>`;
    }

    daysEl.innerHTML = daysHtml;

    // 4. Re-attach click events to the new day elements
    document.querySelectorAll('.day:not(.other-month)').forEach(day => {
        day.addEventListener('click', () => {
            const dateStr = day.getAttribute('data-date');
            const [year, month, dayNum] = dateStr.split('-').map(Number);
            selectedDate = new Date(year, month - 1, dayNum);
            
            // Re-render so the 'selected' class moves to the right day
            renderCalendar(); 
            // Update the panel on the right
            showEvents(dateStr); 
        });
    });
}

    function showEvents(dateStr) {
        const [year, month, day] = dateStr.split('-').map(Number);
        const dateObj = new Date(year, month - 1, day);
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

        eventDateEl.textContent = `${dayNames[dateObj.getDay()]}, ${months[dateObj.getMonth()]} ${day}, ${year}`;
        eventListEl.innerHTML = '';

        const dayEvents = events[dateStr] || [];

        if (dayEvents.length > 0) {
            dayEvents.forEach(event => {
                const eventItem = document.createElement('div');
                eventItem.className = 'event-item';
                eventItem.innerHTML = `
                    <div class="event-color ${event.color || ''}"></div>
                    <div class="event-time">${event.time}</div>
                    <div class="event-text">${event.text}</div>
                `;
                eventListEl.appendChild(eventItem);
            });
        } else {
            eventListEl.innerHTML = '<div class="no-events">No events scheduled for this day</div>';
        }
    }

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    todayBtn.addEventListener('click', () => {
        currentDate = new Date();
        selectedDate = new Date();
        renderCalendar();
        const dateStr = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${currentDate.getDate()}`;
        showEvents(dateStr);
    });

    renderCalendar();
});