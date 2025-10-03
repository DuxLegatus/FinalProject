const urlParams = new URLSearchParams(window.location.search);
const scheduleId = urlParams.get("schedule");

const scheduleDiv = document.getElementById("scheduleDetails");
const seatList = document.getElementById("seatList");
const bookingForm = document.getElementById("bookingForm");
const msgEl = document.getElementById("message");

const seatModal = document.getElementById("seatModal");
const closeModal = document.getElementById("closeModal");
const chooseSeatBtn = document.getElementById("chooseSeatBtn");
const carriageList = document.getElementById("carriageList");
const seatGrid = document.getElementById("seatGrid");

const navList = document.getElementById("nav-list");
const logoutNav = document.getElementById("logout")

let selectedSeatId = null;
let allSeats = [];
let selectedCarriage = null;

let schedule = null;

async function fetchSchedule() {
    try {
        const res = await fetch(`http://127.0.0.1:8000/Train/train-schedule/${scheduleId}/`);
        if (!res.ok) throw new Error("Failed to fetch schedule");
        schedule = await res.json();

        scheduleDiv.innerHTML = `
      <h3>Train: ${schedule.train.name}</h3>
      <p><strong>From:</strong> ${schedule.starting_location}</p>
      <p><strong>To:</strong> ${schedule.final_destination}</p>
      <p><strong>Departure:</strong> ${new Date(schedule.departure_date).toLocaleString()}</p>
      <p><strong>Arrival:</strong> ${new Date(schedule.arrival_time).toLocaleString()}</p>
      <p><strong>Status:</strong> ${schedule.status}</p>
      
      
    `;
    } catch (err) {
        scheduleDiv.textContent = "Error: " + err;
    }
}


async function fetchSeats() {
    try {
        const res = await fetch(`http://127.0.0.1:8000/Train/seats/?schedule=${scheduleId}`);
        if (!res.ok) throw new Error("Failed to fetch seats");
        const data = await res.json();
        allSeats = data.results;

        const token = localStorage.getItem("access_token");
        const bookedRes = await fetch(`http://127.0.0.1:8000/Booking/bookings/?schedule_id=${scheduleId}`, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });
        const bookedData = await bookedRes.json();
        console.log(bookedData)
        const bookedSeats = bookedData.results ? bookedData.results : bookedData;
        const bookedSeatIds = bookedSeats.map(b => b.seat.id);


        const carriages = [...new Set(allSeats.map(s => s.carriage))];
        carriageList.innerHTML = "";
        carriages.forEach(c => {
            const btn = document.createElement("button");
            btn.textContent = "Carriage " + c;
            btn.addEventListener("click", () => showSeatsForCarriage(c, bookedSeatIds));
            carriageList.appendChild(btn);
        });

    } catch (err) {
        carriageList.textContent = "Error: " + err;
    }
}

function showSeatsForCarriage(carriageNum, bookedSeatIds) {
    selectedCarriage = carriageNum;
    seatGrid.innerHTML = "";

    const seats = allSeats.filter(s => s.carriage === carriageNum);
    seats.forEach(seat => {
        const div = document.createElement("div");
        div.classList.add("seat");

        const classType = seat.class_type;
        const basePrice = schedule.price
        const price = classType === "first" ? (basePrice * 1.5).toFixed(2) : basePrice.toFixed(2);
        const priceEl = document.createElement("span");
        priceEl.textContent = `$${price}`;
        priceEl.classList.add("seat-price");
        div.appendChild(priceEl);
        if (bookedSeatIds.includes(seat.id)) {
            div.classList.add("booked");
        } else {
            div.addEventListener("click", () => {
                document.querySelectorAll(".seat").forEach(s => s.classList.remove("selected"));
                div.classList.add("selected");
                selectedSeatId = seat.id;
            });
        }

        seatGrid.appendChild(div);
    });
}


chooseSeatBtn.addEventListener("click", () => {
    seatModal.style.display = "flex";
});

closeModal.addEventListener("click", () => {
    seatModal.style.display = "none";
});

window.addEventListener("click", (e) => {
    if (e.target === seatModal) {
        seatModal.style.display = "none";
    }
});


bookingForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!selectedSeatId) {
        msgEl.style.color = "red";
        msgEl.textContent = "Please select a seat first!";
        return;
    }

    const data = {
        schedule_id: scheduleId,
        seat_id: selectedSeatId,
        first_name: document.getElementById("first_name").value,
        last_name: document.getElementById("last_name").value,
        personal_number: document.getElementById("personal_number").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
    };

    try {
        const token = localStorage.getItem("access_token");
        const res = await fetch("http://127.0.0.1:8000/Booking/bookings/", {
            method: "POST",  
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(data) 
        });

        const result = await res.json();
        console.log(result);

        if (res.ok) {
            const bookingData = {
                ticket_id: result.ticket.id,
                ticket_number: result.ticket.ticket_number,
                seat_number: result.seat.seat_number,
                first_name: result.first_name,
                last_name: result.last_name,
                price: result.price
            };
            localStorage.setItem("bookingData", JSON.stringify(bookingData));

            msgEl.style.color = "green";
            msgEl.textContent = "Booking successful! Redirecting to payment...";
            setTimeout(() => window.location.href = "pay.html", 1500);
        } else {
            msgEl.style.color = "red";
            msgEl.textContent = JSON.stringify(result);
        }
    } catch (err) {
        msgEl.style.color = "red";
        msgEl.textContent = "Error: " + err;
    }
});

function GetTicket(scheduleId) {
    window.location.href = `pay.html?schedule=${scheduleId}`;
}
async function logout() {
  const access = localStorage.getItem("access_token");
  const refresh = localStorage.getItem("refresh_token");
  if (!access) return;

  try {
    const res = await fetch("http://127.0.0.1:8000/user/logout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${access}`
      },
      body: JSON.stringify({ refresh })
    });
    if (res.ok) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      renderNav();
    }
    else {
      console.error("Logout failed:", await res.json());
    }


  } catch (error) {
    console.error("Logout failed", error);
  }
}


function renderNav() {
  const token = localStorage.getItem("access_token");

  navList.querySelectorAll(".auth-link")?.forEach(el => el.remove());

  if (token) {
    const profileLi = document.createElement("li");
    profileLi.classList.add("auth-link");
    profileLi.innerHTML = `<a href="#" class="profile-link"></a>`;

    const logoutLi = document.createElement("li");
    logoutLi.classList.add("auth-link");
    logoutLi.innerHTML = `<a href="#">Sign Out</a>`;
    logoutLi.addEventListener("click", logout);

    navList.appendChild(profileLi);
    navList.appendChild(logoutLi);
  } else {

    const registerLi = document.createElement("li");
    registerLi.classList.add("auth-link");
    registerLi.innerHTML = `<a href="register.html">Register</a>`;

    const loginLi = document.createElement("li");
    loginLi.classList.add("auth-link");
    loginLi.innerHTML = `<a href="login.html">Login</a>`;

    navList.appendChild(registerLi);
    navList.appendChild(loginLi);
  }
}

renderNav();

fetchSchedule();
fetchSeats();
