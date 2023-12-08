function removeFromCart(productId) {
    // Send a POST request to remove the product
    fetch(`/remove-product/${productId}`, {
        method: "POST",
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        return response.json();
        
    })
    .then(data => {
        // Optionally handle the response data if needed
        console.log(data);
            location.reload()
    })
    .catch(error => {
        console.error('Error in fetch request:', error);
        // Log the error details to the console
        console.log(error.message);
        // You can display an error message to the user here if needed
        alert('Error removing the product. Please try again.');
    });
}

// Add a click event listener to the "Remove" buttons
document.querySelectorAll(".remove-from-cart").forEach(function(button) {
    button.addEventListener("click", function() {
        // Get the product ID from the data attribute
        const productId = this.dataset.productId;
        removeFromCart(productId);
    });
});