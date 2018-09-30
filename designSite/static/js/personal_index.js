function get_circuits(name, authority) {
    $.get('/api/authority_circuits', {name:JSON.stringify(name)}, function (res) {
        if (res.circuits.length > 0) {
            $('#circuits-modal div h5').html(`Ciruit Name: ${name}`);
            let html = 
            `<thead>
                <tr>
                    <th class="sorted descending">ID</th>
                    <th class="sorted descending">Editor</th>
                    <th class="sorted descending">Update Time</th>
                    <th class="sorted descending">Comment</th>
                </tr>
            </thead>`
            $('#circuits-table').append(html);
            res.circuits.forEach(element => {
                $('#circuits-table').append(
                    `<tbody data-id="${element.ID}">
                        <td>${element.ID}</td>
                        <td>${element.Editor}</td>
                        <td>${element.UpdateTime}</td>
                        <td>${element.Comment}</td>
                    </tbody>`
                );
            });
            $('#circuits-table').children('tbody').on('click', function () {
                let id = $(this).attr('data-id');
                let url = `/design/${id}`;
                if (authority === 'share-table') {
                    url = `/design/share/${id}`;
                }
                window.location = url;
            });
        } else {
            $('#circuits-table').html('<h5 class="ui center aligned">Empty!</h5>');
        }
    });
}

$(function () {
    $('#master-table, #share-table').children('tbody').on('click', function () {
        let name = $(this).attr('data-name');
        get_circuits(name, $(this).parent()[0].id);
        $('#circuits-modal').modal({
            onHide: function() {
                $('#circuits-table').html('');
            }
        }).modal('show');
    });
});

$('#logout').on('click', function () {
    window.location.href = '/logout';
});

$('.tabular.menu .item').tab();