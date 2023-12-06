function updateProduct(productId) {
    // Fetch values from the edit form
    var productName = $('#editProductName').val();
    var productDetails = $('#editProductDetails').val();
    var category = $('#editCategory').val();
    var price = $('#editPrice').val() || 0;  // Use 0 if price is undefined
    var quantity = $('#editQuantity').val();
    var productImage = $('#editProductImage')[0].files[0];  // Fetch the selected file

    // Prepare form data for AJAX request
    var formData = new FormData();
    formData.append('product_name', productName);
    formData.append('product_details', productDetails);
    formData.append('category', category);
    formData.append('price', price);
    formData.append('quantity', quantity);
    formData.append('product_image', productImage);  // Append the file to the form data

    // Make an AJAX request to update the product
    $.ajax({
        type: 'POST',
        url: '/update_product_ajax/' + productId,
        data: formData,
        contentType: false,  // Set content type to false for FormData
        processData: false,  // Prevent jQuery from processing the data
        success: function (response) {
            if (response.status === 'success') {
                // Optionally, update the UI with the new product details
                // You may also close the edit modal if needed
                $('#editModal' + productId).modal('hide');
                // You can update the UI or refresh the page as per your requirements
            } else {
                console.log("Update failed: " + response.message);
                // Handle the case where updating was not successful
            }
        },
        error: function (xhr, status, error) {
            console.log("An error occurred while processing the request.");
            console.log(xhr.responseText);
        }
    });
}
