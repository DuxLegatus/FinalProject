const navList = document.getElementById("nav-list");
const logoutNav = document.getElementById("logout")
document.addEventListener("DOMContentLoaded", async () => {
  const ticketsList = document.getElementById("tickets-list");
  const token = localStorage.getItem("access_token");

  try {
    const res = await fetch("http://127.0.0.1:8000/Booking/tickets/", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("Failed to load tickets");

    const data = await res.json();
    const tickets = data.results || data;

    if (tickets.length === 0) {
      ticketsList.innerHTML = "<p>You don’t have any tickets yet.</p>";
      return;
    }

    ticketsList.innerHTML = "";
    tickets.forEach(ticket => {
      const card = document.createElement("div");
      card.classList.add("ticket-card");

      card.innerHTML = `
        <div class="ticket-info">
          <p><strong>Ticket #:</strong> ${ticket.ticket_number}</p>
          <p><strong>Name:</strong> ${ticket.booking.first_name} ${ticket.booking.last_name}</p>
          <p><strong>Seat:</strong> Carriage ${ticket.booking.seat.carriage}, Seat ${ticket.booking.seat.seat_number}</p>
          <p><strong>Schedule:</strong> ${ticket.booking.schedule.train.name} 
             (${ticket.booking.schedule.starting_location} → ${ticket.booking.schedule.final_destination})</p>
          <p><strong>Date:</strong> ${ticket.booking.schedule.departure_date}</p>
          <p><strong>Price:</strong> ${ticket.booking.price} GEL</p>
          <p><strong>Status:</strong> ${ticket.is_outdated ? "Outdated" : "Active"}</p>
        </div>
        <div class="ticket-actions">
          <button onclick="downloadTicket(${ticket.id})">Download PDF</button>
          <button onclick="refundTicket(${ticket.id}, this)">Refund</button>
        </div>
      `;

      ticketsList.appendChild(card);
    });

  } catch (err) {
    ticketsList.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
  }
});

async function refundTicket(ticketId, button) {
  const token = localStorage.getItem("access_token");

  if (!confirm("Are you sure you want to refund this ticket?")) return;

  try {
    const res = await fetch(`http://127.0.0.1:8000/Booking/ticket/${ticketId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || "Failed to refund ticket");

    alert(data.detail);
    button.closest(".ticket-card").remove();

  } catch (err) {
    alert("Error: " + err.message);
  }
}

async function downloadTicket(ticketId) {
  const token = localStorage.getItem("access_token");
  try {
    const res = await fetch(`http://127.0.0.1:8000/Booking/ticket/${ticketId}/pdf/`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("Failed to download ticket");

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ticket_${ticketId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();

  } catch (err) {
    alert("Error: " + err.message);
  }
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