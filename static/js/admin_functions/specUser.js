// get the ID of the user 

document.addEventListener("click", function (event) {
    if (event.target.classList.contains("view-more-button")) {
        const userId = event.target.getAttribute("data-user-id");
        redirectToUserPage(userId);
    }
});

function redirectToUserPage(userId) {
    // Construct the URL with the user's ID
    const userPageURL = `/user/${userId}`;

    // Redirect to the user's page
    window.location.href = userPageURL;
}