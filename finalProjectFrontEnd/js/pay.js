
const bookingData = JSON.parse(localStorage.getItem("bookingData"));
const msgEl = document.getElementById("message");
const payBtn = document.getElementById("payBtn");
const downloadBtn = document.getElementById("downloadBtn");


if (bookingData) {
    document.getElementById("ticketInfo").innerHTML = `
        <p><strong>Name:</strong> ${bookingData.first_name} ${bookingData.last_name}</p>
        <p><strong>Seat Number:</strong> ${bookingData.seat_number}</p>
        <p><strong>Price:</strong> $${bookingData.price.toFixed(2)}</p>
        <p><strong>Ticket Number:</strong> ${bookingData.ticket_number}</p>
    `;
} else {
    msgEl.style.color = "red";
    msgEl.textContent = "No booking found. Please go back and book a seat first.";
    payBtn.disabled = true;
    downloadBtn.disabled = true;
}

payBtn.addEventListener("click", () => {
    msgEl.style.color = "green";
    msgEl.textContent = "Payment successful! You can now download your ticket.";
    downloadBtn.disabled = false;
});


downloadBtn.addEventListener("click", async () => {
    try {
        const token = localStorage.getItem("access_token");
        const res = await fetch(`http://127.0.0.1:8000/Booking/ticket/${bookingData.ticket_id}/pdf/`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error("Failed to fetch ticket PDF");

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Ticket_${bookingData.ticket_number}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);

        localStorage.removeItem("bookingData");

        msgEl.textContent = "Ticket downloaded successfully!";
    } catch (err) {
        msgEl.style.color = "red";
        msgEl.textContent = "Error downloading ticket PDF: " + err;
    }
});
