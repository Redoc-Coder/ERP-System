// Get references to the button and badge
const addToCartButton = document.getElementById("add-to-cart-button");
const cartBadge = document.getElementById("cart-badge");

// Initialize the cart count
let cartCount = 0;

// Add a click event listener to the "Add to Cart" button
addToCartButton.addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the default link behavior

  // Increment the cart count
  cartCount++;

  // Update the badge value
  cartBadge.textContent = cartCount;
});