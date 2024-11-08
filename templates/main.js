$(document).ready(function() {
    function showModal(message) {
        $('#modalMessage').text(message);
        $('#notificationModal').modal('show');
    }

    $('.add-to-favourites').on('click', function(e) {
        e.preventDefault();

        var productId = $(this).data('product-id');

        $.ajax({
            url: "{{ url_for('add_to_favourite.add_to_favourites') }}",
            type: 'POST',
            data: {
                'product_id': productId
            },
            success: function(response) {
                if (response.message) {
                    showModal(response.message);
                }
            },
            error: function(xhr, status, error) {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    showModal(xhr.responseJSON.error);
                } else {
                    showModal('An error occurred. Please try again.');
                }
            }
        });
    });

    $('.add-to-cart').on('click', function(e) {
        e.preventDefault();

        var productId = $(this).data('product-id');
        var quantity = $(this).data('quantity') || 1;

        $.ajax({
            url: "{{ url_for('add_to_cart.add_to_cart') }}",
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': quantity
            },
            success: function(response) {
                if (response.message) {
                    showModal(response.message);
                }
            },
            error: function(xhr, status, error) {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    showModal(xhr.responseJSON.error);
                } else {
                    showModal('An error occurred. Please try again.');
                }
            }
        });
    });
});
function submitForm() {
    document.getElementById('search-bar').submit();
}
function googleTranslateElementInit() {
    new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
}