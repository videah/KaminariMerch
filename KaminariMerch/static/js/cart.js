$(document).ready(function() {

    function remove_from_cart(id) {

        $.post('/remove_from_cart', {
            id: id
        }).done(function () {
            location.reload();
        })

    }

    $('.remove-button').click(function () {
        $this = $(this);
        remove_from_cart($this.val())
    });

});