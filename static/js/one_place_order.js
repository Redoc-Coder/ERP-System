    document.addEventListener('DOMContentLoaded', function () {
        // Find the element with the class 'place-order-button'
        var placeOrderButton = document.querySelector('.place-order-button');

        // Attach a click event listener to the button
        placeOrderButton.addEventListener('click', function () {
        // Get the product ID from the data-product-id attribute
        var productId = placeOrderButton.dataset.productId;
        var address = document.getElementById('address').value;
        var paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;


        // Send an AJAX request to the server
        fetch('/one_place_order', {
            method: 'POST',
            headers: {  
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({
            productId: productId,
            address: address,
            paymentMethod: paymentMethod,
            }),
        })
            .then(response => response.json())
            .then(data => {
            // Handle the response, you can redirect or show a success message
            console.log(data.message);
            })
            .catch(error => {
            // Handle errors
            console.error('Error:', error);
            });
        });
    });