$(document).ready(function() {

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    function mark_order_as_paid() {
        $('#tick').show();
        $('#tick-trigger').addClass('drawn');
        $('#qr-code').hide();
        $('.small').hide();
        $('.btn').hide();
    }

    socket.on('connect', function() {
        socket.emit('subscribe', {order: $('#check-button').val() });
    });

    socket.on('confirm_payment', function() {
       mark_order_as_paid();
    });


    $('#check-button').click(function() {

        $this = $(this);

        $.post('/check_payment', {
            id: $this.val()
        }).done(function(data) {

            if (data.paid === true) {
                mark_order_as_paid()
            }

        });
    });

    // https://codepen.io/shaikmaqsood/pen/XmydxJ
    function copyToClipboard(element) {
        var $temp = $("<input>");
        $("body").append($temp);
        $temp.val($(element).text()).select();
        document.execCommand("copy");
        $temp.remove();
    }

    $('#copy-button').click(function() {
        copyToClipboard('#payment-request')
    });

});