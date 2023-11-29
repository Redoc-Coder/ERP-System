document.addEventListener("DOMContentLoaded", function () {
    const quantityInputs = document.querySelectorAll('.quantity');

    quantityInputs.forEach(function (input) {
      input.addEventListener('input', function () {
        const productId = input.getAttribute('data-product-id');
        const newQuantity = input.value;

        // Send the updated quantity to the server using AJAX
        updateQuantity(productId, newQuantity);
      });
    });

    function updateQuantity(productId, newQuantity) {
      // Use AJAX to send the updated quantity to the server
      // You can use Fetch API or other methods to send a POST request
      fetch('/update_quantity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId: productId,
          newQuantity: newQuantity,
        }),
      })
        .then(response => response.json())
        .then(data => {
          // Handle the server response if needed
          console.log(data);
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }
  });