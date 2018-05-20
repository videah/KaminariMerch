$(document).ready(function() {

    function item_success(button) {

        // Fancy effect for the cart icon. Gives some nice feedback to the user.
        $('.cart-icon').effect('shake', {times: 2, distance: 5, direction: 'up'});

        button.switchClass('btn-primary', 'btn-success');
        button.prop('disabled', true);
        button.text('Added To Cart');

    }

    function item_failure(button) {

        button.switchClass('btn-primary', 'btn-danger');
        button.text('Error: Could Not Add');

    }

    function add_to_cart(id) {

        $.post('/add_to_cart', {
            id: id
        }).done(function() {
            item_success($this);
        }).fail(function() {
            item_failure($this);
        })

    }

    // The Product ID is pulled from the button and passed to server to add to the session's cart.
    $('.item-button').click(function() {
        $this = $(this);
        add_to_cart($this.val())
    });

});