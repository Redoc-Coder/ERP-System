document.addEventListener("DOMContentLoaded", function () {
    // Initialize the overallTotal variable to keep track of the total
    var overallTotal = 0;

    // Function to update the overall total
    function updateOverallTotal() {
        // Reset the overallTotal
        overallTotal = 0;

        // Loop through all the product rows
        document.querySelectorAll('.row').forEach(function (productRow) {
            // Get the product ID
            var productId = productRow.getAttribute('data-product-id');

            // Get the total for this product
            var totalElement = document.querySelector('#total-' + productId);
            if (totalElement) {
                var total = parseFloat(totalElement.textContent.replace('₱', '').trim());

                // Add the product total to the overall total
                overallTotal += total;
            }
        });

        // Update the overall total element with the new value, including the "₱" symbol
        document.getElementById('overall-total').textContent = 'Total Price: ₱' + overallTotal.toFixed(2);
    }

    // Initialize the overall total on page load
    updateOverallTotal();

    // Add an event listener to the parent element that contains all the products
    document.querySelector('#cart-container').addEventListener('input', function (event) {
        if (event.target.classList.contains('quantity')) {
            // Get the product ID
            var productId = event.target.closest('.row').getAttribute('data-product-id');

            // Get the quantity input value
            var quantity = parseInt(event.target.value);

            // Get the default price from the total span and convert it to a number
            var defaultPriceElement = event.target.closest('.row').querySelector('.description-cont p:nth-child(2)');
            if (defaultPriceElement) {
                var defaultPrice = parseFloat(defaultPriceElement.textContent);
                
                // Check if defaultPrice is a valid number
                if (!isNaN(defaultPrice)) {
                    // Calculate the total
                    var total = quantity * defaultPrice;

                    // Update the total element with the new value
                    var totalElement = document.querySelector('#total-' + productId);
                    if (totalElement) {
                        totalElement.textContent = '₱' + total.toFixed(2);
                    }

                    // Update the overall total
                    updateOverallTotal();
                }
            }
        }
    });
});