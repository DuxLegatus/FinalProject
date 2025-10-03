const form = document.getElementById("searchForm");
const resultsDiv = document.getElementById("results");
const navList = document.getElementById("nav-list");
const logoutNav = document.getElementById("logout")

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const starting_location = document.getElementById("starting_location").value;
  const final_destination = document.getElementById("final_destination").value;
  const departure_date = document.getElementById("departure_date").value;

  try {
    const response = await fetch(`http://127.0.0.1:8000/Train/train-schedules/?starting_location=${starting_location}&final_destination=${final_destination}&departure_date=${departure_date}`);

    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.json();

    const schedules = data.results || data;

    resultsDiv.innerHTML = "";

    schedules.forEach(schedule => {
      const div = document.createElement("div");
      div.classList.add("result-card");
      div.innerHTML = `
            <h3>Train: ${schedule.train.name}</h3>
            <p><strong>From:</strong> ${schedule.starting_location}</p>
            <p><strong>To:</strong> ${schedule.final_destination}</p>
            <p><strong>Departure:</strong> ${new Date(schedule.departure_date).toLocaleString()}</p>
            <p><strong>Arrival:</strong> ${new Date(schedule.arrival_time).toLocaleString()}</p>
            <p><strong>Status:</strong> ${schedule.status}</p>
            <button onclick="bookTrain(${schedule.id})">Book</button>
        `;

      resultsDiv.appendChild(div);
    });

  } catch (error) {
    resultsDiv.textContent = "Error fetching train schedules: " + error;
  }
});
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

document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const from = urlParams.get("from");
  const to = urlParams.get("to");

  if (from && to) {

    document.getElementById("starting_location").value = from;
    document.getElementById("final_destination").value = to;

    document.getElementById("searchForm").dispatchEvent(new Event("submit"));
  }
});
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

function bookTrain(scheduleId) {
  const token = localStorage.getItem("access_token");
  if (token){
    window.location.href = `passenger.html?schedule=${scheduleId}`;
  }
  else{
    window.location.href = `register.html`;
  }
  
}
