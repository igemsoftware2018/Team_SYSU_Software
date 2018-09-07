$('#login-form')
    .form({
        fields: {
            username: ['empty'],
            password: ['empty']
        }
    });
$('#signin-button')
    .on('click', function () {
        $('#login-form')
            .form('submit');
    });