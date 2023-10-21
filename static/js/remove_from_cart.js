function removeFromCart(productId) {
    // Send a POST request to remove the product
    fetch(`/remove-from-cart/${productId}`, {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Product removed from cart successfully") {
            // If the removal was successful, remove the product element from the page
            const productElement = document.querySelector(`[data-product-id="${productId}"]`);
            productElement.remove();
        }
    })
    .catch(error => {
        console.error("Error:", error);
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