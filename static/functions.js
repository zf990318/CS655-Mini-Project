$(document).ready(function () {
    // Init
    $('.image-section');
    $('#result');

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        readURL(this);
    });

    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        $.ajax({
            type: 'POST',
            data: form_data,
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