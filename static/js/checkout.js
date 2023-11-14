document.addEventListener("DOMContentLoaded", function () {
  document.getElementById('placeOrderButton').addEventListener('click', function () {
    placeOrder();
  });

  function placeOrder() {
    var productIds = [];

    // Assuming product IDs are stored as data attributes
    var productElements = document.querySelectorAll('.product');
    productElements.forEach(function(productElement) {
      productIds.push(productElement.getAttribute('data-product-id'));
    });

    // Make an AJAX request to the server to place the order
    fetch('/place_order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ productIds: productIds }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      // Optionally, you can redirect or show a success message to the user
    })
    .catch((error) => {
      console.error('Error:', error);
      // Optionally, you can show an error message to the user
    });
  }
});