function addToCart(productId) {
    // Send a POST request to add the product
    fetch(`/add-to-cart/${productId}`, {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Product added to cart successfully") {
            // Update the cart badge by fetching the cart count
            fetch("/get-cart-count")
                .then(response => response.json())
                .then(cartData => {
                    // Update the cart badge with the new count
                    const cartBadge = document.getElementById("cart-badge");
                    cartBadge.textContent = cartData.count;
                })
                .catch(error => {
                    console.error("Error fetching cart count:", error);
                });
        } else if (data.error === "Product already in cart") {
            // Show the modal if the product is already in the cart
            const productExistsModal = new bootstrap.Modal(document.getElementById('productExistsModal'));
            productExistsModal.show();
        } else {
            console.error("Error:", data.error);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

// Add a click event listener to the "Add to Cart" buttons
document.querySelectorAll(".add-cart").forEach(function(button) {
    button.addEventListener("click", function() {
        // Get the product ID from the data attribute
        const productId = this.dataset.productId;
        addToCart(productId);
    });
});