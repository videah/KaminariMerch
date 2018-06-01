$(document).ready(function() {

    $('#comment-btn').click(function() {
        $.post('/post/' + $('#comment-btn').val() + '/post_comment', {
            comment: $('#comment-box').val()
        }).done(function() {
            $('#comment-box').val('');
        })
    })

});