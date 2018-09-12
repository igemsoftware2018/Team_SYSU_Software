$(function () {
    $('#master-table').children('tbody').on('click', function () {
        let id = $(this).attr('data-id');
        let url = `/design/${id}`;
        window.location = url;
    });
    $('#share-table').children('tbody').on('click', function () {
        let id = $(this).attr('data-id');
        let url = `/design/share/${id}`;
        window.location = url;
    });
});

$('#logout').on('click', function () {
    window.location.href = '/logout';
});
$('#design-button').on('click', function () {
    window.location.href = '/design';
});

$('.tabular.menu .item').tab();