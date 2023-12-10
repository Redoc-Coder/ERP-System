document.addEventListener("DOMContentLoaded", function () {
    const quantityInput = document.getElementById('quantity');
    const incrementButton = document.getElementById('increment');
    const decrementButton = document.getElementById('decrement');

    incrementButton.addEventListener('click', function () {
      // Increment the quantity
      quantityInput.value = parseInt(quantityInput.value) + 1;

      // Make an AJAX request to update the order_quantity in the backend
      updateOrderQuantity(quantityInput.value);
    });

    decrementButton.addEventListener('click', function () {
      // Ensure the quantity doesn't go below 1
      if (parseInt(quantityInput.value) > 1) {
        // Decrement the quantity
        quantityInput.value = parseInt(quantityInput.value) - 1;

        // Make an AJAX request to update the order_quantity in the backend
        updateOrderQuantity(quantityInput.value);
      }
    });
    const quantityButton = document.getElementById('quantityButton');
    const productId = quantityButton.getAttribute('data-product-id');
    function updateOrderQuantity(newQuantity) {
      // Make an AJAX request to update the order_quantity in the backend
      fetch('/update_order_quantity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId: productId, 
          newOrderQuantity: newQuantity,
        }),
      });
    }
  });
