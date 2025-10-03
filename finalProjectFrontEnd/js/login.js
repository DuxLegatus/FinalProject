const navList = document.getElementById("nav-list");
const logoutNav = document.getElementById("logout")
document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        username: document.getElementById("username").value,
        password: document.getElementById("password").value
    };

    const msgEl = document.getElementById("message");

    try {
        const response = await fetch("http://127.0.0.1:8000/user/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", result.access);
            localStorage.setItem("refresh_token", result.refresh);

            msgEl.style.color = "green";
            msgEl.textContent = "Login successful!";
            
            window.location.href = "search.html";
        } else {
            msgEl.style.color = "red";
            msgEl.textContent = result.detail || "Login failed!";
        }
    } catch (error) {
        msgEl.style.color = "red";
        msgEl.textContent = "Server error: " + error;
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



function renderNav() {
  const token = localStorage.getItem("access_token");

  navList.querySelectorAll(".auth-link")?.forEach(el => el.remove());

  if (token) {
    const profileLi = document.createElement("li");
    profileLi.classList.add("auth-link");
    profileLi.innerHTML = `<a href="#" class="profile-link">Profile</a>`;

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