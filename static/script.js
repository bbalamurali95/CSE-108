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
    };
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
        console.log("Raw response:", this.responseText);
        console.log("Status: ", this.status);

        if (this.status === 200) {
            window.location.href = "/";
        } else {
            alert(this.responseText);
        }
    };
}

document.addEventListener("DOMContentLoaded", function () {
    const monthYearEl = document.getElementById("month-year");
    const daysEl = document.getElementById("days");
    const prevMonthBtn = document.getElementById("prev-month");
    const nextMonthBtn = document.getElementById("next-month");
    const todayBtn = document.getElementById("today-btn");
    const eventDateEl = document.getElementById("event-date");
    const eventListEl = document.getElementById("event-list");

    if (!monthYearEl || !daysEl || !prevMonthBtn || !nextMonthBtn || !todayBtn || !eventDateEl || !eventListEl) {
        return;
    }

    let currentDate = new Date(2026, 4, 1);
    let selectedDate = new Date(2026, 4, 13);

    const events = {
        "2026-5-1": [
            { time: "5:30 PM", text: "Club Meeting", color: "club" }
        ],
        "2026-5-8": [
            { time: "5:30 PM", text: "Street Fighter Casuals", color: "street" }
        ],
        "2026-5-13": [
            { time: "4:00 PM", text: "Tekken 8 Tournament", color: "tekken" }
        ],
        "2026-5-15": [
            { time: "5:30 PM", text: "Club Meeting", color: "club" }
        ],
        "2026-5-22": [
            { time: "5:30 PM", text: "Guilty Gear Night", color: "guilty" }
        ],
        "2026-5-29": [
            { time: "5:30 PM", text: "Club Meeting", color: "club" }
        ]
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

        for (let x = firstDayIndex; x > 0; x--) {
            const prevDate = prevLastDay.getDate() - x + 1;
            daysHtml += `<div class="day other-month">${prevDate}</div>`;
        }

        for (let i = 1; i <= lastDay.getDate(); i++) {
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
            const dateKey = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${i}`;
            const dayEvents = events[dateKey] || [];

            let dayClass = "day";

            if (date.toDateString() === new Date().toDateString()) {
                dayClass += " today";
            }

            if (selectedDate && date.toDateString() === selectedDate.toDateString()) {
                dayClass += " selected";
            }

            if (dayEvents.length > 0) {
                dayClass += " has-events";
            }

            let dotsHtml = "";

            if (dayEvents.length > 0) {
                dotsHtml += '<div class="event-dots-container">';

                for (let j = 0; j < dayEvents.length; j++) {
                    dotsHtml += `<div class="dot ${dayEvents[j].color}"></div>`;
                }

                dotsHtml += "</div>";
            }

            daysHtml += `
                <div class="${dayClass}" data-date="${dateKey}">
                    ${i}
                    ${dotsHtml}
                </div>
            `;
        }

        for (let j = 1; j <= nextDays; j++) {
            daysHtml += `<div class="day other-month">${j}</div>`;
        }

        daysEl.innerHTML = daysHtml;

        document.querySelectorAll(".day:not(.other-month)").forEach(function(day) {
            day.addEventListener("click", function() {
                const dateStr = day.getAttribute("data-date");
                const parts = dateStr.split("-").map(Number);
                selectedDate = new Date(parts[0], parts[1] - 1, parts[2]);
                renderCalendar();
                showEvents(dateStr);
            });
        });
    }

    function showEvents(dateStr) {
        const parts = dateStr.split("-").map(Number);
        const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);

        const months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];

        const dayNames = [
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ];

        eventDateEl.textContent = `${dayNames[dateObj.getDay()]}, ${months[dateObj.getMonth()]} ${parts[2]}, ${parts[0]}`;
        eventListEl.innerHTML = "";

        const dayEvents = events[dateStr] || [];

        if (dayEvents.length > 0) {
            for (let i = 0; i < dayEvents.length; i++) {
                const eventItem = document.createElement("div");
                eventItem.className = "event-item";

                eventItem.innerHTML = `
                    <div class="event-color ${dayEvents[i].color}"></div>
                    <div class="event-time">${dayEvents[i].time}</div>
                    <div class="event-text">${dayEvents[i].text}</div>
                `;

                eventListEl.appendChild(eventItem);
            }
        } else {
            eventListEl.innerHTML = '<div class="no-events">No events scheduled for this day</div>';
        }
    }

    prevMonthBtn.addEventListener("click", function() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener("click", function() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    todayBtn.addEventListener("click", function() {
        currentDate = new Date();
        selectedDate = new Date();
        renderCalendar();

        const dateStr = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${currentDate.getDate()}`;
        showEvents(dateStr);
    });

    renderCalendar();

    const startingDate = `${selectedDate.getFullYear()}-${selectedDate.getMonth() + 1}-${selectedDate.getDate()}`;
    showEvents(startingDate);
});




document.addEventListener("DOMContentLoaded", function() {
    const observerOptions = {
        threshold: 0.2 
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
              
                const textboxes = entry.target.querySelectorAll('.game-header,.game-textbox, .game-description');
                textboxes.forEach(el => el.classList.add('animate-in'));
                
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

   
    const gameSections = document.querySelectorAll('.game');
    gameSections.forEach(section => {
        observer.observe(section);
    });
});