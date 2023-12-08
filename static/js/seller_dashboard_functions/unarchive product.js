   document.addEventListener('DOMContentLoaded', function() {
       const addButtons = document.querySelectorAll('.add-product-btn');

       addButtons.forEach(button => {
           button.addEventListener('click', function() {
               const productId = this.dataset.productId;
               const sellerId = this.dataset.sellerId;

               // Send a POST request to add the product
               fetch(`/add-product/${productId}`, {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                   },
                   body: JSON.stringify({ seller_id: sellerId }),
               })
               .then(response => {
                   if (!response.ok) {
                       throw new Error(`Error: ${response.status} ${response.statusText}`);
                   }
                   return response.json();
               })
               .then(data => {
                   // Optionally handle the response data if needed
                   console.log(data);
                   // Reload the page after successful addition
                   location.reload();
               })
               .catch(error => {
                   console.error('Error in fetch request:', error);
                   // Log the error details to the console
                   console.log(error.message);
                   // You can display an error message to the user here if needed
                   alert('Error adding the product. Please try again.');
               });
           });
       });
   });