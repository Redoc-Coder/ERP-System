
  // Add a click event listener to the "Add to Cart" button
  document.querySelectorAll(".add-to-cart").forEach(function (button) {
    button.addEventListener("click", function () {
        // Get product data from hidden input fields
        const productName = this.parentElement.querySelector(".product-name").value;
        const productPrice = this.parentElement.querySelector(".product-price").value;

        // Create a new FormData object to send to the server
        const formData = new FormData();
        formData.append("product_name", productName);
        formData.append("product_price", productPrice);

        // Send a POST request to add the product to the cart
        fetch("/add-to-cart", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response from the server
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
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});


//remove
