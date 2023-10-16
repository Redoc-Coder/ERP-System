 // Initialize the cart count
 let cartCount = 0;

 // Function to update the cart badge
 function updateCartBadge() {
     const cartBadge = document.getElementById("cart-badge");
     cartBadge.textContent = cartCount;
 }

 // Add a click event listener to all buttons with the class "add-to-cart"
 const addToCartButtons = document.querySelectorAll(".add-to-cart");
 addToCartButtons.forEach(function (button) {
     button.addEventListener("click", function () {
         // Increment the cart count
         cartCount++;
         // Update the cart badge
         updateCartBadge();
     });
 });