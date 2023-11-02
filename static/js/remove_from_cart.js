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
      // Fetch the updated total price
      fetch("/get-total-price")
      .then(response => response.json())
      .then(totalPriceData => {
          // Update the displayed total price
          const totalPriceElement = document.getElementById("total-price");
          totalPriceElement.textContent = `₱${totalPriceData.total_price}.00`;
      })
      .catch(error => {
          console.error("Error fetching total price:", error);
      });


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