$(document).ready(function () {

    $('.ui.form')
        .form({
            fields: {
                username: ['empty'],
                // username: {
                //     identifier: 'username', 
                //     rules: [{
                //         type: "empty",
                //         prompt: "Username format invalid."
                //     }]
                // },
                email: ['email', 'empty'],
                password: ['minLength[6]', 'empty'],
                password2: ['match[password]'],
                org: ['empty'],
                igem: ['email']
            }
        });

    $('#register-button')
        .on('click', function () {
            $('.ui.form').form('submit');
        });
    $('#login-button')
        .on('click', function () {
            window.location.href = '/login';
        });

    $('#policy').on('click', () => {
        $('#policy-modal').modal('show');
    });
    $('#cancel').on('click', () => {
        $('#policy-modal').modal('hide');
    });

})