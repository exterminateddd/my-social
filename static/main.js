$(document).ready(function() {

    $('.updateButton').on('click', function() {

        var member_id = $(this).attr('member_id');

        var name = $('#nameInput'+member_id).val();
        var email = $('#emailInput'+member_id).val();

        req = $.ajax({
            url : '/add_post',
            type : 'POST',
            data : { title : name, email : email }
        });

        req.done(function(data) {

            $('#memberSection'+member_id).fadeOut(1000).fadeIn(1000);
            $('#memberNumber'+member_id).text(data.member_num);

        });

    });

});