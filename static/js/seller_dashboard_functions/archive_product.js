$(document).ready(function () {
    $('.delete-product').click(function () {
        var productId = $(this).data('product-id');
        var currentRow = $(this).closest('tr'); // Store the reference to the current row
        var currentModal = $(this).closest('.modal'); // Find the closest modal within the parent

        $.ajax({
            type: 'POST',
            url: '/delete_product_ajax/' + productId,
            success: function (response) {
                if (response.status === 'success') {
                    // Remove the deleted row from the table
                    currentRow.remove();
                    // Trigger Bootstrap modal hide event and remove the modal from the DOM
                    currentModal.on('hidden.bs.modal', function () {
                        $(this).remove();
                    }).modal('hide');
                } else {
                    // Handle the case where deletion was not successful
                    console.log("Deletion failed: " + response.message);
                }
            },
            error: function (xhr, status, error) {
                // Handle AJAX error
                console.log("An error occurred while processing the request.");
                console.log(xhr.responseText);
            }
        });
    });
});