function redirectTo(url) {
    window.location.href = url;
  }

  document.addEventListener("DOMContentLoaded", function() {
    // Attach event listeners to your sidebar links.
    const sidebarLinks = document.querySelectorAll(".sidebar-link");
    sidebarLinks.forEach(function(link) {
        link.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent the default link behavior (e.g., navigating to a new page).

            const pageURL = link.getAttribute("data-page");

            // Fetch the content of the new page.
            fetch(pageURL)
                .then(response => response.text())
                .then(data => {
                    // Update the content-container with the loaded content.
                    document.getElementById("content-container").innerHTML = data;
                })
                .catch(error => {
                    console.error("Error loading content:", error);
                });
        });
    });
});