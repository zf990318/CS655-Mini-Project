
//functions that read image file and trigger button
$(document).ready(function () {
    $('.image-section');
    $('#result');

    // Upload image and display preview of it
    function readFile(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imageView').css('background-image', 'url(' + e.target.result + ')');
                $('#imageView').fadeIn(300);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    //Show image preview and submit button after upload image
    $("#upload").change(function () {
        $('.image-section').show();
        $('#submit-button').show();
        readFile(this);
    });

    //Display predict result of submit image
    $('#submit-button').click(function () {
        var image_input = new FormData($('#image-file')[0]);

        $.ajax({
            type: 'POST',
            data: image_input,
            contentType: false,
            processData: false,
            async: true,
            timeout: 300,
            success: function (data) {
                $('#result').fadeIn(100);
                $('#result').text(data);
            },
        });
    });

});