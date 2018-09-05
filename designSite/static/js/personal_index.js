$(function() {
    $('#circuit-card').children('.ui.segment').on('click', function() {
        let id = $(this).attr('data-id');
        let url = `/design/${id}`;
        window.location = url;
    });
});