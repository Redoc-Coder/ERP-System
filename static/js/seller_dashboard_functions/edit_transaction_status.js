$(document).ready(function () {
    $('.update-status').on('click', function (e) {
        e.preventDefault();

        // Store a reference to 'this'
        var $this = $(this);

        var orderId = $this.closest('.users-item-dropdown').data('order-id');
        var newStatus = $this.data('status');

        $.ajax({
            type: 'POST',
            url: '/update_order_status/' + orderId + '/' + newStatus,
            success: function (response) {
                if (response.success) {
                    // Update the status in the UI
                    var badge = $this.closest('tr').find('.badge-pending');
                    badge.text(newStatus);
                    console.log('Order status updated successfully.');
                } else {
                    console.error('Failed to update order status.');
                }
            },
            error: function () {
                console.error('Failed to send AJAX request.');
            }
        });
    });
});