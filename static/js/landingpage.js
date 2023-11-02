var cards = document.querySelectorAll(".clickable-card");

// Add a click event listener to each card
cards.forEach(function(card) {
    card.addEventListener("click", function(event) {
        // Check if the click occurred on the "Add to Cart" button
        if (!event.target.closest("#addToCartButton")) {
  
            window.location.href = "/product-info";
        }
    });
});