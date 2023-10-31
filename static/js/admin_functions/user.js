function redirectToUserPage() {

  window.location.href = "/admin/user";
}
//search users
document.getElementById("searchInput").addEventListener("input", function () {
  const searchTerm = this.value.toLowerCase();
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach((row) => {
    const emailCell = row.querySelector("td:nth-child(3)");
    const email = emailCell.textContent.toLowerCase();

    if (email.startsWith(searchTerm)) {
      row.style.display = "table-row";
    } else {
      row.style.display = "none";
    }
  });
});