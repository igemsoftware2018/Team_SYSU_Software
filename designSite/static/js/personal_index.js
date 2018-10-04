function get_circuits(name, authority) {
    $.get('/api/authority_circuits', {
        name: JSON.stringify(name)
    }, function (res) {
        if (res.circuits.length > 0) {
            $('#circuits-modal div h5').html(`Ciruit Name: ${name}`);
            let html =
                `<thead>
                <tr>
                    <th class="sorted descending">ID</th>\
                    <th class="sorted descending">Editor</th>\
                    <th class="sorted descending">Update Time</th>\
                    <th class="sorted descending">Comment</th>\
                `
            // if (authority !== 'share-table') {
            //     html += `<th class="sorted descending">Authority Manage</th>`;
            // }
            html += `</tr></thead>`

            $('#circuits-table').append(html);
            res.circuits.forEach(element => {
                let temp = `<tbody data-id="${element.ID}">\
                    <td class="id">${element.ID}</td>\
                    <td>${element.Editor}</td>\
                    <td>${element.UpdateTime}</td>\
                    <td>${element.Comment}</td>`;
                // if (authority !== 'share-table') {
                //     temp += `<td class="ui small button" style="z-index=100">Authority Manage</td>`;
                // }
                $('#circuits-table').append(temp + `</tbody>`);
            });
            $('#circuits-table').children('tbody').on('click', function () {
                let id = $(this).attr('data-id');
                let url = `/design/${id}`;
                if (authority === 'share-table') {
                    url = `/design/share/${id}`;
                }
                window.location = url;
            });
            // $('#circuits-table').children('tbody').children('tr').children('.button').on('click', function () {
            //     console.log("manage");
            // });
        } else {
            $('#circuits-table').html('<h5 class="ui center aligned">Empty!</h5>');
        }
    });
}

let id;
function refresh() {
    $.get('/api/authority?circuit=' + id, function (res) {
        if (res.read.length > 0) {
            $('#view-users').html(`<div class="ui list">`);
            res.read.forEach(function (ele) {
                $('#view-users').append(
                    `<div class="item">
                        <div class="content">
                            <i class="users icon"></i>${ele}<i class="red delete icon authority-delete"></i>
                        </div>
                        <div class="ui divider"></div>
                    </div>`);
            });
            $('#view-users').append(`</div>`);
        } else {
            $('#view-users').html('<h5 class="ui center aligned">Share your design to others!</h5>');
        }
        if (res.write.length > 0) {
            $('#edit-users').html(`<div class="ui list">`);
            res.write.forEach(function (ele) {
                $('#edit-users').append(
                    `<div class="item">
                        <div class="content">
                            <i class="users icon"></i>${ele}<i class="red delete icon authority-delete"></i>
                        </div>
                        <div class="ui divider"></div>
                    </div>`);
            });
            $('#edit-users').append(`</div>`);
        } else {
            $('#edit-users').html('<h5 class="ui center aligned">Share your design to others!</h5>');
        }

        $('.authority-delete').on('click', function () {
            let username = $(this).parent()[0].innerText;
            $.ajax({
                type: 'DELETE',
                url: '/api/authority_delete',
                data: {
                    'username': username,
                    'design': id,
                },
                success: (res) => {
                    // res.status == 0 -> error
                    // res.status == 1 -> success
                    refresh(id);
                    alert(res.msg);
                }
            })
        });
    });
}

$('#search-users-dropdown').dropdown({
    apiSettings: {
        url: '/api/users?username={query}',
        cache: false,
        beforeSend: (settings) => {
            return settings.urlData.query.length < 1 ? false : settings;
        },
        onResponse: (response) => ({
            success: response.success === true,
            results: response.users.map((x) => ({
                name: x.username,
                value: x.username
            }))
        })
    }
}).popup({
    content: 'Search a user (Case Sensitive)'
});
$('#share-view-button, #share-edit-button').on('click', function (event) {
    if ($('#search-users-dropdown').dropdown('get value').length > 0) {
        let data = {
            users: JSON.stringify($('#search-users-dropdown').dropdown('get value')),
            circuit: JSON.stringify(id),
            authority: JSON.stringify(
                event.target.innerText === 'Share view' ? 'read' : 'write'
            )
        };
        $.post('/api/authority', data, function (v) {
            refresh();
            alert(v.msg);
        });
    }
});

$(function () {
    $('#master-table, #share-table').children('tbody').on('click', function () {
        let name = $(this).attr('data-name');
        get_circuits(name, $(this).parent()[0].id);
        $('#circuits-modal').modal({
            onHide: function () {
                $('#circuits-table').html('');
            }
        }).modal('show');
    });

    $('#authority-table').children('tbody').on('click', function () {
        id = $(this).attr('data-id');
        refresh();
        $('#share-tab .item').tab();
        $('#share-modal').modal({
            onHide: function () {
                $('#search-users-dropdown').dropdown('clear');
            }
        }).modal('show');
    });
});

$('#logout').on('click', function () {
    window.location.href = '/logout';
});

$('.tabular.menu .item').tab();