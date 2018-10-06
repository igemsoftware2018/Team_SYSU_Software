'use strict';

/* eslint-disable no-console */
/* global SDinDesign, Chart, html2canvas echarts*/

$.getScript('/static/js/echarts.js');

let NUM_OF_TYPE = 20;

let designId = $('#canvas-box').attr('design-id');
let design;

let CHASSIS;
let CHASSIS_FORMAT;

let save_mode = 0;

let username = $('#username-hack').text();
let authorname = $('#authorname-hack').text();

let $design_msg_modal = $('#design-msg-modal');
let $design_msg_body = $('#design-msg-body');

$design_msg_modal.modal({
    allowMultiple: true
});
$('.ui.modal').modal({
    allowMultiple: true
});
$.ajax({
    type: 'GET',
    url: '/api/chassis',
    async: false,
    success: (res) => {
        CHASSIS = res.chassis;
        CHASSIS_FORMAT = res.chassis_format;
    }
});



// Hide save button when creating a new design
$(function () {
    let t = window.location.href.split('/');
    if (t[t.length - 1] == "design" || (t[t.length - 2] == "design" && t[t.length - 1] == ""))
        $("#save-button").hide();
})


if (designId !== '' && parseInt(designId) !== -1) {
    // $.get(`/api/circuit?id=${designId}`, (value) => {
    //     design = new SDinDesign('#canvas', value);
    // });
    $.ajax(`/api/circuit?id=${designId}`, {
        type: 'GET',
        async: false,
        success: function (value) {
            design = new SDinDesign('#canvas', value);

        }
    });
} else
    design = new SDinDesign('#canvas');

$('.left.sidebar').first().sidebar('attach events', '#operation');


function protocolShuffleStepID() {
    let $mp = $('#protocol-step-mountpoint');
    $mp.children().each((idx, ele) => {
        let $ele = $(ele);
        $ele.find('span').html(`step ${idx + 1}`);
    });
}

function protocolAddLastStepHook() {
    $('#protocol-step-mountpoint').children().last().find('i[name=protocol-step-delete]').on('click', function () {
        $(this).parent().parent().remove();
        protocolShuffleStepID();
    });
}

const protocolStepHelper = (i) => {
    return `
    <div class="field">
        <div class="ui horizontal divider header" >
        <span> step ${i+1} </span>
        <i class="ui icon delete" name="protocol-step-delete"></i>
        </div>

        <div class="field">
            <label> title </label>
            <input type="text" />
            <label> body </label>
            <textarea rows="3" ></textarea>
        </div>
    </div>
    `;
};
// protocol button
$('#protocol-step-add').on('click', function () {
    let $mountpoint = $('#protocol-step-mountpoint');
    let length = $mountpoint.children().length;
    $mountpoint.append(protocolStepHelper(length));
    // add delete hook here
    protocolAddLastStepHook();

});
$(function () {
    $('#protocol-step-add').click();
});
$('#protocol-submit').on('click', function () {
    let $m = $('#protocol-modal');
    design._design.protocol.title = $m.find('[name=title]').val();
    design._design.protocol.description = $m.find('[name=description]').val();
    let $mp = $('#protocol-step-mountpoint');
    let step_titles = $mp.find('input');
    let step_desc = $mp.find('textarea');

    // WARNING: this zip only use here. never use elsewhere.
    const zip = (iter1, iter2) => {
        let ret = [];
        for (let idx = 0; idx < iter1.length; ++idx) {
            ret.push([iter1.eq(idx), iter2.eq(idx)]);
        }
        return ret;
    };
    design._design.protocol.steps = [];
    let id = 0;
    for (let item of zip(step_titles, step_desc)) {
        design._design.protocol.steps.push({
            id: id++,
            title: item[0].val(),
            body: item[1].val()
        });
    }
    $m.parent().click();

});
$('#protocol-button')
    .on('click', () => {
        $('#protocol-modal').modal('show');
    })
    .popup({
        content: 'Add your Protocol'
    });
function __protocol_refresh_from_design() {
    let $m = $('#protocol-modal');
    $m.find('[name=title]').val(design._design.protocol.title);
    $m.find('[name=description]').val(design._design.protocol.description);
    let $mp = $('#protocol-step-mountpoint');
    let step_titles = $mp.find('input');
    let step_desc = $mp.find('textarea');

    let pl = design.design.protocol.steps.length;
    let ml = step_titles.length;
    let diff = pl - ml;
    const min = (a, b) => (a < b ? a : b);
    let base = min(pl, ml);
    if (diff > 0) {
        for (let i = 0; i < diff; ++i) {
            $mp.append(protocolStepHelper(base + i));
            protocolAddLastStepHook();
        }
    } else if (diff < 0) {
        for (let i = 0; i < -diff; ++i) {
            $mp.children().eq(base).remove();
        }
    }
    let new_step_titles = $mp.find('input');
    let new_step_desc = $mp.find('textarea');
    for (let i = 0; i < pl; ++i) {
        new_step_titles.eq(i).val(design.design.protocol.steps[i].title);
        new_step_desc.eq(i).val(design.design.protocol.steps[i].body);
    }
}
//  __trigger: one click dimmer one, onHide trigger twice.
// use this method to only run it once.
let __trigger = false;
$('#protocol-modal').modal({
    dimmerSettings: {
        onHide: function () {
            if (!__trigger) {
                __trigger = true;
                return;
            }
            __trigger = false;
            __protocol_refresh_from_design();
        }
    }
});


// Upload file
function new_to_old(data) {

    // Get parts infomation
    var Lines = [],
        Devices = [],
        Parts = [];
    var cid_dict = {};
    $.each(data.components, function (index, component) {
        cid_dict[component.name] = design._nextPartCid;
        design._nextPartCid = design._nextPartCid + 1;
        $.ajax({
            type: 'GET',
            url: '/api/parts?flag=11111111111111111111&name=' + component.name,
            async: false,
            success: function (res) {
                $.ajax({
                    type: 'GET',
                    url: '/api/part?id=' + res.parts[0].id,
                    async: false,
                    success: function (res2) {
                        let temp = {
                            id: res.parts[0].id,
                            cid: cid_dict[component.name],
                            name: component.name,
                            description: component.description,
                            type: res2.type,
                            X: 0,
                            Y: 0
                        };
                        Parts.push(temp);
                    }
                });
            }
        });
    });


    $.each(data.stimulations, function (index, stimulation) {
        let temp = {
            start: cid_dict[stimulation.stimulator],
            end: cid_dict[stimulation.other],
            type: 'stimulation'
        };
        Lines.push(temp);
    });
    $.each(data.inhibitions, function (index, inhibition) {
        let temp = {
            start: cid_dict[inhibition.inhibitor],
            end: cid_dict[inhibition.other],
            type: 'inhibition'
        };
        Lines.push(temp);
    });
    $.each(data.lines, function (index, line) {
        let Subparts = [];
        let x = -214;
        let y = -180;
        $.each(line.structure, function (index, x) {
            Subparts.push(cid_dict[x]);
        });
        let temp = {
            subparts: Subparts,
            X: x,
            Y: y + index * 110
        };
        Devices.push(temp);
    });
    let result = {
        id: -1,
        combines: [],
        lines: Lines,
        devices: Devices,
        parts: Parts
    };
    return result;
}

let JsonFileReader = new FileReader();
JsonFileReader.onload = () => {
    console.log(new_to_old(JSON.parse(JsonFileReader.result)));
    design.design = new_to_old(JSON.parse(JsonFileReader.result));
};
let sbolFileReader = new FileReader();
sbolFileReader.onload = () => {
    // console.log(sbolFileReader.result);
    let data = {
        data: sbolFileReader.result
    };
    $.post('/api/sbol_json', data, function (v) {
        console.log(v['data']);
        let temp = new_to_old(JSON.parse(v['data']));
        console.log(temp);
        design.design = temp;
    });
};
$('#upload-button').on('click', function () {
    $('#fileupload').trigger('click');
}).popup({
    content: 'Import a JSON file as design.'
});
$('#fileupload').on('change', function () {
    JsonFileReader.readAsText($('#fileupload')[0].files[0]);
});

$('#sbol-json-button').on('click', function () {
    $('#sbolfileupload').trigger('click');
}).popup({
    content: 'Import a SBOL file as your design'
});
$('#sbolfileupload').on('change', function () {
    let data = $('input[name="sbolfiles[]"]')[0].files[0];
    sbolFileReader.readAsText(data);
});

//export file
function old_to_new(old) {
    var Components = [];
    var Lines = [];
    var Stimulations = [];
    var Inhibitions = [];
    var part_dict = {};
    $.each(old.parts, function (index, part) {
        $.ajax({
            type: 'GET',
            url: '/api/part?id=' + part.id,
            async: false,
            success: function (res) {
                let Role = res.role;
                let Sequence = res.sequence;
                let temp = {
                    role: Role,
                    id: part.id,
                    name: part.name,
                    version: '1',
                    description: part.description,
                    sequence: Sequence
                };
                Components.push(temp);
            }
        });
        part_dict[part.cid] = part.name;
    });
    $.each(old.devices, function (index, device) {
        let temp = {
            name: 'gene_' + index,
            structure: []
        };
        $.each(device.subparts, function (index, subpart) {
            temp.structure.push(part_dict[subpart]);
        });
        Lines.push(temp);
    });
    $.each(old.lines, function (index, line) {
        if (line.type == 'inhibition') {
            let temp = {
                'inhibitor': part_dict[line.start],
                'other': part_dict[line.end]
            };
            Inhibitions.push(temp);
        } else if (line.type == 'promotion' || line.type == 'stimulation') {
            let temp = {
                'stimulator': part_dict[line.start],
                'other': part_dict[line.end]
            };
            Stimulations.push(temp);
        }
    });
    let data = {
        components: Components,
        lines: Lines,
        stimulations: Stimulations,
        inhibitions: Inhibitions,
        circuit: {
            id: old.id,
            name: old.name === undefined ? 'unnamed' : old.name,
            description: ''
        }
    };
    return data;
}

function createJsonDownload(fileName, content) {
    let aLink = $('<a></a>');
    aLink
        .attr('download', fileName)
        .attr('href', `data:application/json;base64,${btoa(JSON.stringify(content))}`);
    aLink[0].click();
}
$('#export-button').on('click', () => {
    let filename;
    if (design.name === undefined || design.name === '')
        filename = 'unnamed_design.json';
    else
        filename = `${design.name}.json`;
    createJsonDownload(filename, old_to_new(design.design));
}).popup({
    content: 'Export your design as a JSON.'
});

$('#json-sbol-button').on('click', function () {
    let data = {
        data: JSON.stringify(old_to_new(design.design))
    };
    console.log(data);
    $.post('/api/sbol_doc', data, function (res) {
        console.log(res);
        let filename = 'yours.xml';
        var blob = new Blob([(new XMLSerializer).serializeToString(res)], {
            type: 'application/xml'
        });
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;

        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);
    });
}).popup({
    content: 'Export your design as a SBOL file'
});

// Analysis view
$('#analysis-button').on('click', function () {

    $('#analysis-modal').modal({
        onShow: function () {
            let data = [];
            let unique = {};
            let parts = design.design.parts;
            $.each(parts, function (index, part) {
                if (!unique[part.name]) {
                    data.push({
                        name: part.name,
                        value: part.id
                    });
                    unique[part.name] = 1;
                }
            });
            $('#analysis-part-dropdown').dropdown({
                values: data,
                onChange: function (value) {
                    $.get('/api/part?id=' + value, function (res) {
                        $('#selected-part-sequence').text(res.sequence);
                    });
                }
            });
        },
        onHide: function () {
            $('#analysis-sequence').val('');
            $('#selected-part-sequence').text('Selected Part Sequence here');
            echarts.dispose(document.getElementById('myChart'));
        }
    }).modal('show');
}).popup({
    content: 'Analysis your design.'
});
$('#add-to-sequence-button').on('click', function () {
    let seq = $('#selected-part-sequence').html();
    console.log(seq);
    $('#analysis-sequence').val(function (i, text) {
        return text + seq;
    });
});
let selected_chassis;
let selected_chassis_mode;
$('#analysis-chassis-dropdown').dropdown(
    (function () {
        let ret = {
            values: []
        }
        CHASSIS.forEach(function (element) {
            ret.values.push({
                name: element,
                value: element,
            })
        })
        ret.values[0].selected = true;
        ret.onChange = function (value) {
            selected_chassis = value;
        }
        return ret;
    })()
);


$('#analysis-chassis-mode-dropdown').dropdown(
    (function () {
        let ret = {
            values: []
        }
        CHASSIS_FORMAT.forEach(function (element) {
            ret.values.push({
                name: element,
                value: element,
            })
        })
        ret.values[0].selected = true;
        ret.onChange = function (value) {
            selected_chassis_mode = value;
        }
        return ret;
    })()
);

$('#analysis-sequence-button').on('click', function () {
    let temp = {
        sequence: $('#analysis-sequence').val(),
        chassis: selected_chassis,
        mode: selected_chassis_mode
    };
    console.log(temp);
    $.post('api/analysis', temp, (res) => {
        if (res.status != 0) {
            $('#analysis-sequence').popup({
                content: res.msg,
                onHide: function () {
                    $('#analysis-sequence').popup('destroy');
                }
            }).popup('show');
        } else {
            let myChart = echarts.init(document.getElementById('myChart'));
            let option = {
                tooltip: {
                    formatter: "{b}:{c}"
                },
                series: [{
                        name: 'CAI',
                        type: 'gauge',
                        radius: '80%',
                        min: 0,
                        max: 100,
                        startAngle: 150,
                        endAngle: 30,
                        splitNumber: 2,
                        axisLine: {
                            lineStyle: {
                                width: 8,
                                color: [
                                    [0.2, '#c23531'],
                                    [0.8, '#63869e'],
                                    [1, '#91c7ae']
                                ]
                            }
                        },
                        axisTick: {
                            splitNumber: 5,
                            length: 10,
                            lineStyle: {
                                color: 'auto'
                            }
                        },
                        axisLabel: {
                            fontWeight: 'bold',
                            fontSize: '15',
                            formatter: function (v) {
                                switch (v + '') {
                                    case '0':
                                        return '0';
                                    case '50':
                                        return '50%\nCAI';
                                    case '100':
                                        return '100%';
                                }
                            }
                        },
                        splitLine: {
                            length: 15,
                            lineStyle: {
                                color: 'auto'
                            }
                        },
                        title: {
                            show: false
                        },
                        detail: {
                            show: false
                        },
                        data: [{
                            value: res.CAI,
                            name: 'CAI'
                        }]
                    },
                    {
                        name: 'CG',
                        type: 'gauge',
                        radius: '80%',
                        min: 0,
                        max: 100,
                        startAngle: 330,
                        endAngle: 210,
                        splitNumber: 2,
                        axisLine: {
                            lineStyle: {
                                width: 8,
                                color: [
                                    [1, '#63869e']
                                ]
                            }
                        },
                        axisTick: {
                            splitNumber: 5,
                            length: 10,
                            lineStyle: {
                                color: 'auto'
                            }
                        },
                        axisLabel: {
                            fontWeight: 'bold',
                            fontSize: '15',
                            formatter: function (v) {
                                switch (v + '') {
                                    case '0':
                                        return '0';
                                    case '50':
                                        return 'CG\n50%';
                                    case '100':
                                        return '100%';
                                }
                            }
                        },
                        splitLine: {
                            length: 15,
                            lineStyle: {
                                color: 'auto'
                            }
                        },
                        title: {
                            show: false
                        },
                        detail: {
                            show: false
                        },
                        data: [{
                            value: res.CG,
                            name: 'CG'
                        }]
                    }
                ]
            };
            myChart.setOption(option);
        }
    });
});


// Share
$('#share-button').popup({
    content: 'Share your design'
});

function refresh() {
    $.get('/api/authority?circuit=' + design._id, function (res) {
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
        $('.authority-delete').on('click', function() {
            let username = $(this).parent()[0].innerText;
            if (design._id == -1) {
                alert("Please save your design first!");
                return;
            }
            let id = design._id;
            $.ajax({
                type: 'DELETE',
                url: '/api/authority_delete',
                data: {
                    'username': username,
                    'design': id,
                },
                success: (res) => {
                    $design_msg_modal.modal('show');
                    setTimeout(() => {
                        $design_msg_modal.modal('hide');
                    }, 1000);
                    // res.status == 0 -> error
                    // res.status == 1 -> success
                    refresh();
                    // alert(res.msg);
                }
            })
        });
    });
}

$('#share-button').on('click', function () {
    refresh();
    $('#share-tab .item').tab();
    $('#share-modal').modal({
        onHide: function () {
            $('#search-users-dropdown').dropdown('clear');
        }
    }).modal('show');
});
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
    if (design._id == -1) {
        $design_msg_body.text('ERROR. Please save your design first.');
        $design_msg_modal.modal('show');
        setTimeout(() => {
            $design_msg_body.modal('hide');
        }, 3000);
    } else if ($('#search-users-dropdown').dropdown('get value').length > 0) {
        $design_msg_body.text('Connecting to the server...');
        $design_msg_modal.modal('show');
        let data = {
            users: JSON.stringify($('#search-users-dropdown').dropdown('get value')),
            circuit: JSON.stringify(design._id),
            authority: JSON.stringify(
                event.target.innerText === 'Share view' ? 'read' : 'write'
            )
        };
        $.post('/api/authority', data, function (v) {
            refresh();
            $design_msg_body.text(v.msg)
            setTimeout(() => {
                $design_msg_modal.modal('hide');
            }, 1000);
        });
    }
});


$('#save-button').on('click', () => {
    save_mode = 0;
    $('#save-circuit-name').val(design.name);
    $('#save-circuit-description').val(design.description);
    $('#save-modal').modal('show');
}).popup({
    content: 'Save your design to server.'
});
$('#save-as-new-button').on('click', function () {
    save_mode = 1;
    if (!$('#save-as-new-circuit-name').val()) {
        $('#save-as-new-circuit-name').attr("placeholder", design.name);
    }
    $('#save-as-new-modal').modal('show');

}).popup({
    content: 'Save as a new design to the server'
});

$('#save-circuit, #save-as-new-circuit').on('click', () => {
    $('#save-modal, #save-as-new-modal').modal('hide');
    $('.ui.dimmer:first .loader')
        .text('Saving your circuit to server, please wait...');
    $('.ui.dimmer:first').dimmer('show');
    // design._design.name = $('#save-as-new-circuit-name').val();
    // design._design.description = $('#save-as-new-circuit-description').val();
    let postData = design.design;
    postData.comment = $('#update-comment').val();
    postData.id = save_mode == 0 ? design._id : -1;
    if (postData.id === -1) {
        postData.description = $('#save-as-new-circuit-description').val();
        postData.name = $('#save-as-new-circuit-name').val();
    }
    // postData.circuit = {
    //     id: (save_mode == 0 ? design._id: -1),
    //     description 
    //     comment = $('#update-comment').val()
    // };
    postData = {
        data: JSON.stringify(postData),
        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
    };
    $.post('/api/circuit', postData, (v) => {
        if (v.status === 1)
            $('.ui.dimmer:first .loader').text(`Success, circuit ID = ${v.circuit_id}, closing...`);
        else
            $('.ui.dimmer:first .loader').text((v.status == -1 ? v.error_msg : 'Failed, closing...'));
        setTimeout(() => {
            $('.ui.dimmer:first').dimmer('hide');
        }, 3000);

        // Redirect to the new design
        if (v.status === 1)
            window.location.replace(`/design/${v.circuit_id}`);
    });
});

$('#load-button').on('click', () => {
    $('.ui.dimmer:first .loader')
        .text('Querying your circuit from server, please wait...');
    $('.ui.dimmer:first').dimmer('show');
    $.get('/api/get_saves', (v) => {
        $('.ui.dimmer:first').dimmer('hide');
        $('#load-modal>.content>.user-circuits').html('');
        if (v.circuits.length > 0) {
            let filter_data = [];
            let unique = {};
            v.circuits.forEach((c) => {
                let html = `
                    <div class="ui segment" data-id=${c.id} data-name=${c.name}>
                        <p><b>ID: </b>${c.id}</p>
                        <p><b>Name: </b>${c.name}</p>
                        <p><b>Description: </b>${c.description}</p>
                        <p><b>Version: </b><!--TODO: Version--></p>
                    </div>`;
                $('#load-modal>.content>.user-circuits').append(html);
                if (!unique[c.name]) {
                    filter_data.push({
                        name: c.name,
                        value: c.name
                    });
                    unique[c.name] = 1;
                }
            });
            $('#circuit-filter-dropdown').dropdown({
                values: filter_data, 
                onChange: function (value) {
                    if (value != '') {
                        $('#load-modal .segment').each(function (index, item) {
                            // console.log($(this).data('name'));
                            if ($(this).data('name') != value) {
                                $(this).attr("style", "display:none;");
                            } else {
                                $(this).attr("style", "display:block;");
                            }
                        });
                    } else {
                        $(this).attr("style", "display:block;");
                    }
                }
            });
            $('#filter-clear').on('click', function () {
                $('#circuit-filter-dropdown').dropdown('clear');
                $('#load-modal .segment').each(function (index, item) {
                    $(this).attr("style", "display:block;");
                });
            });
            $('#load-modal .segment').on('click', function () {
                let id = $(this).data('id');
                $('#load-modal').modal('hide');
                $('.ui.dimmer:first .loader')
                    .text(`Loading ${id} from server, please wait...`);
                $('.ui.dimmer:first').dimmer('show');

                // Redirect to a new url when 
                window.location.replace(`/design/${id}`);

                // The following code is useless
                $.get(`/api/circuit?id=${id}`, (value) => {
                    $('.ui.dimmer:first').dimmer('hide');
                    design.design = value;
                    $('#chassis-dropdown').dropdown(
                        'set selected', value.chassis
                    );
                });
            });
        } else {
            $('#load-modal>.content>.user-circuits').append(
                `<h5>Empty.</h5>`
            );
        }
        $('#load-modal').modal('show');
    });
}).popup({
    content: 'Load your circuit from server.'
});

$('#zoom-in').on('click', () => {
    let ratio = design.ratio;
    ratio = Math.max(0.25, Math.min(1.5, ratio + 0.25));
    $('#ratio-dropdown')
        .dropdown('set value', ratio)
        .dropdown('set text', Math.round(ratio * 100) + '%');
    design.ratio = ratio;
}).popup({
    variation: 'flowing popup',
    content: 'Zoom in design. (Alt + Mousewheel up)'
});

$('#zoom-out').on('click', function () {
    let ratio = design.ratio;
    ratio = Math.max(0.25, Math.min(1.5, ratio - 0.25));
    $('#ratio-dropdown')
        .dropdown('set value', ratio)
        .dropdown('set text', Math.round(ratio * 100) + '%');
    design.ratio = ratio;
}).popup({
    variation: 'flowing popup',
    content: 'Zoom out design. (Alt + Mousewheel down)'
});

$('#ratio-dropdown')
    .dropdown({
        values: (() => {
            let values = [];
            for (let i = 25; i < 150; i += 25)
                values.push({
                    name: `${i}%`,
                    value: i / 100,
                    selected: i === 100
                });
            return values;
        })(),
        onChange: function (value, text) {
            if (text === undefined)
                return;
            if ($(this).data('initialized') === undefined) {
                $(this).data('initialized', true);
                return;
            }
            design.ratio = value;
        }
    });


$('#gene-type-dropdown').dropdown({
    values: (function () {
        let ret = []
        SDinDesign.partTypes.forEach(function (element, i) {
            if (SDinDesign.isGene(element))
                ret.push({
                    name: element,
                    value: element,
                })
        })
        ret[0].selected = true;
        return ret;
    }()),
});

$('#material-type-dropdown').dropdown({
    values: (function () {
        let ret = []
        SDinDesign.partTypes.forEach(function (element, i) {
            if (!SDinDesign.isGene(element))
                ret.push({
                    name: element,
                    value: element,
                })
        })
        ret[0].selected = true;
        return ret;
    }()),
})
$('#part-safety-dropdown')
    .dropdown({
        values: SDinDesign.partSafetyLevels.map((x, i) => ({
            name: `${i} - ${x}`,
            value: i,
            selected: i === 0
        }))
    });

$('.tabular.menu>.item')
    .tab({
        context: 'parent'
    });

$('.window')
    .draggable({
        appendTo: 'body',
        handle: '.nav',
        scroll: false,
        stack: '.window'
    })
    .resizable({
        handles: 's, w, sw'
    });

$('#undo-button').on('click', function () {
    design.undo();
    let t = design.canUndo;
    if (t === false)
        t = 'Unable to undo.';
    $(this).popup('get popup').html(t);
}).popup({
    variation: 'small popup',
    content: 'undo',
    onShow: function () {
        let t = design.canUndo;
        if (t === false)
            t = 'Unable to undo.';
        this.html(t);
    }
});
$('#redo-button').on('click', function () {
    design.redo();
    let t = design.canRedo;
    if (t === false)
        t = 'Unable to redo.';
    $(this).popup('get popup').html(t);
}).popup({
    variation: 'small popup',
    content: 'redo',
    onShow: function () {
        let t = design.canRedo;
        if (t === false)
            t = 'Unable to redo.';
        this.html(t);
    }
});

// Part panel

$('#part-panel')
    .resizable('option', 'minWidth', 200);
$('#part-panel-button')
    .on('click', function () {
        if (partPanelCollapsed) {
            uncollapsed();
            $(this).removeClass('left').addClass('right');
        } else {
            if (!partPanelStickedToRight)
                return;
            collapse();
            $(this).removeClass('right').addClass('left');
        }
    })
    .popup({
        content: 'Toggle part panel.'
    });
let partPanelStickedToRight = false;
let partPanelCollapsed = false;

function stickPartPanel() {
    partPanelStickedToRight = true;
    let win = $('#part-panel');
    win
        .resizable('option', 'handles', 'w')
        .draggable('option', 'snap', 'body')
        .draggable('option', 'snapMode', 'inner')
        .draggable('option', 'snapTolerance', 100)
        .draggable('option', 'axis', 'x')
        .on('drag', function (event, ui) {
            if (ui === undefined || ui.helper[0] !== win[0])
                return;
            if (ui.position.left < ui.originalPosition.left - 100) {
                if (partPanelStickedToRight)
                    unstickPartPanel();
            }
        });
    win.data('free-state', {
        height: win.height()
    });
    let toTop = $('.ui.fixed.menu').height();
    win.css({
        transition: 'all 0.2s ease'
    });
    win.css({
        left: $('body').width() - win.width(),
        top: toTop,
        height: 'calc(100% - ' + toTop + 'px)',
        borderRadius: 0,
        border: '',
        borderLeft: '1px solid grey'
    });
    setTimeout(function () {
        win.css({
            transition: ''
        });
    }, 200);
    $('#canvas-box').css({
        width: 'calc(100% - ' + win.width() + 'px)'
    });
    win
        .children('.nav')
        .children('.ui.header').hide();
    $('#part-panel-button')
        .show({
            duration: 200
        });
}

// set this to let the right Penel responsive
$(window).resize(stickPartPanel);

function unstickPartPanel() {
    partPanelStickedToRight = false;
    let win = $('#part-panel');
    let freeState = win.data('free-state');
    win
        .draggable('option', 'snap', 'false')
        .draggable('option', 'snapTolerance', 0)
        .draggable('option', 'axis', 'false')
        .off('drag')
        .resizable('option', 'handles', 'w, s, sw');
    win.css({
        transition: 'all 0.1s ease'
    });
    win.css({
        height: freeState.height,
        borderRadius: '5px',
        border: '1px solid grey'
    });
    $('#canvas-box').css({
        width: '100%'
    });
    setTimeout(function () {
        win.css({
            transition: ''
        });
    }, 100);
    win
        .children('.nav')
        .children('.ui.header').show();
    $('#part-panel-button')
        .hide({
            duration: 100
        });
}

function collapse() {
    partPanelCollapsed = true;
    let win = $('#part-panel');
    win
        .draggable('disable')
        .resizable('disable')
        .css({
            transition: 'left 0.2s ease',
            left: 'calc(100% - 2em)'
        })
        .children('.content')
        .hide();
    $('#part-panel-button')
        .css({
            right: '',
            left: '0.5em'
        });
}

function uncollapsed() {
    partPanelCollapsed = false;
    let win = $('#part-panel');
    win
        .draggable('enable')
        .resizable('enable')
        .css({
            left: $('body').width() - win.width()
        })
        .children('div')
        .show();
    setTimeout(function () {
        win.css({
            transition: ''
        });
    }, 200);
    $('#part-panel-button')
        .css({
            left: '',
            right: '0.5em'
        });
}

$('#advanced-search-button').popup({
    content: 'Search Options'
});

// Initialize the checkboxes
$('#advanced-search-modal .checkbox').checkbox('set checked');


$('.list .master.checkbox')
    .checkbox({
        // check all children
        onChecked: function () {
            var $childCheckbox = $(this).closest('.checkbox').siblings('.list').find('.checkbox');
            $childCheckbox.checkbox('check');
            $childCheckbox.siblings('label').each(function () {
                $(this).removeClass('unchecked').addClass('checked');
            });
        },
        // uncheck all children
        onUnchecked: function () {
            var $childCheckbox = $(this).closest('.checkbox').siblings('.list').find('.checkbox');
            $childCheckbox.checkbox('uncheck');
            $childCheckbox.siblings('label').each(function () {
                $(this).removeClass('checked').addClass('unchecked');
            });
        }
    });



$('.list .child.checkbox')
    .checkbox({
        // Fire on load to set parent value
        fireOnInit: true,
        // Change parent state on each child checkbox change
        onChange: function () {
            let
                $listGroup = $(this).closest('.list'),
                $parentCheckbox = $listGroup.closest('.item').children('.checkbox'),
                $checkbox = $listGroup.find('.checkbox'),
                allChecked = true,
                allUnchecked = true;
            // check to see if all other siblings are checked or unchecked
            $checkbox.each(function () {
                if ($(this).checkbox('is checked')) {
                    allUnchecked = false;
                } else {
                    allChecked = false;
                }
            });
            // set parent checkbox state, but dont trigger its onChange callback
            if (allChecked) {
                $parentCheckbox.checkbox('set checked');
            } else if (allUnchecked) {
                $parentCheckbox.checkbox('set unchecked');
            } else {
                $parentCheckbox.checkbox('set indeterminate');
            }
        },
        onChecked: function () {
            $(this).siblings('label').each(function () {
                $(this).removeClass('unchecked').addClass('checked');
            });
        },
        // uncheck all children
        onUnchecked: function () {
            $(this).siblings('label').each(function () {
                $(this).removeClass('unchecked').addClass('unchecked');
            });
        }
    });





$('#search-parts-dropdown').dropdown({
    apiSettings: {
        url: '/api/parts?flag={target}&name={query}',
        cache: false,
        beforeSend: (settings) => {
            settings.urlData.target = (() => {
                let searchTarget = "";
                let $choices = $('.list .child.checkbox');
                $choices.each(function () {
                    searchTarget += $(this).checkbox('is checked') ? "1" : "0";
                })
                return searchTarget;
            })();
            return settings.urlData.query.length < 3 ? false : settings;
        },
        onResponse: (response) => ({
            success: response.success === true,
            results: response.parts.map((x) => ({
                name: x.name,
                value: x.id
            }))
        })
    },
    onChange: (value) => {
        setPartPanel(value);
    }
}).popup({
    content: 'Search for a part (Case Sensitive)'
});


// Advanced Searching

$('#advanced-search-button').click(function () {
    $('#advanced-search-modal').modal('show');
});



let selectedPart;
let selectedPartHelper = $('<div></div>');

function setPartPanel(id) {
    if (selectedPart !== undefined && selectedPart.id === id) {
        $('#part-info-tab').transition({
            animation: 'flash',
            duration: '0.5s'
        });
        return;
    }
    $.get(`/api/part?id=${id}`, (data) => {
        if (data.success !== true) {
            console.error(`Get part info failed. ID: ${id}`);
            return;
        }
        selectedPart = data;
        $('#part-info-img')
            .attr('src', `/static/img/design/${data.type.toLowerCase()}.png`)
            .draggable('enable')
            .popup({
                content: 'Drag this part into canvas!'
            });
        $('#part-info-name')
            .add(selectedPartHelper.children('b'))
            .text(data.name);
        $('#part-type').text(data.type);
        selectedPartHelper
            .children('div')
            .children('img').attr('src', `/static/img/design/${data.type.toLowerCase()}.png`);
        $('#part-info-des>p').text(data.description);
        $('#show-part-src-seg-button').show();
    });
}
$('#show-part-src-seg-button').on('click', function () {
    $('#source-circuit-modal').modal('show');
    $('#source-list').html('');
    selectedPart.works.forEach((w) => {
        $('#source-list').append(`<li><a href="/work?id=${w.id}">${w.year}-${w.teamname}</li></a>`);
    });
    selectedPart.papers.forEach((p) => {
        $('#source-list').append(`<li><a href="/paper?id=${p.id}">${p.title}</li></a>`);
    });
});
selectedPartHelper
    .addClass('part-helper')
    .append('<b></b>')
    .prepend('<div></div>').children('div')
    .addClass('ui tiny image')
    .append('<img></img>').children('img')
    .attr('src', '/static/img/design/unknown.png');
$('#part-info-img')
    .draggable({
        revert: 'invalid',
        revertDuration: 200,
        helper: () => selectedPartHelper,
        start: () => {
            $('.SDinDesign-subpartDropper').css({
                backgroundColor: 'rgba(255, 0, 0, 0.1)'
            });
        },
        stop: () => {
            $('.SDinDesign-subpartDropper').css({
                backgroundColor: ''
            });
        }
    })
    .draggable('disable');
$('#part-panel-dropper')
    .droppable({
        accept: '#part-panel',
        tolerance: 'touch',
        over: function () {
            $('#part-panel-dropper').css({
                backgroundColor: '#9ec5e6'
            });
        },
        out: function () {
            $(this).css({
                backgroundColor: 'transparent'
            });
        },
        drop: function () {
            stickPartPanel();
            $(this).css({
                backgroundColor: 'transparent'
            });
        }
    });
$('#part-panel')
    .on('resize', function () {
        let des = $('#part-info-des');
        $('#part-panel').css({
            minHeight: 'calc(' + (des.position().top + des.parent().position().top + des.height() + 1) + 'px + 2em)'
        });
        if (partPanelStickedToRight) {
            $('#canvas-box').css({
                width: 'calc(100% - ' + $('#part-panel').width() + 'px)'
            });
        }
    });


$('.ui.dimmer:first').dimmer({
    closable: false
});

function initPositionSize() {
    stickPartPanel();
    $('#fav-win').css({
        height: $(this).height()
    });
}
initPositionSize();

$('#add-part-button').on('click', function () {
    $('#choose-added-part-type').modal('show');
}).popup({
    variation: 'flowing popup',
    content: 'Add your custom gene or material into our database!'
});

let addedPartType; // 0 -- Gene, 1 -- Material

$('#add-gene-button').on('click', function () {
    $('#choose-added-part-type').modal('hide');
    addedPartType = 0;
    $('#new-gene-modal').modal('show');
})

$('#add-material-button').on('click', function () {
    $('#choose-added-part-type').modal('hide');
    addedPartType = 1;
    $('#new-material-modal').modal('show');
})


$('#add-new-gene, #add-new-material')
    .on('click', function () {
        let data;
        if (addedPartType == 0)
            data = {
                name: $('#gene-name').val(),
                description: $('#gene-description').val(),
                type: $('#gene-type-dropdown').dropdown('get value'),
                sequence: $('#gene-sequence').val(),
                subparts: []
            }
        else
            data = {
                name: $('#material-name').val(),
                description: $('#material-description').val(),
                type: $('#material-type-dropdown').dropdown('get value'),
                sequence: "",
                subparts: [],
            }

        $('#new-gene-modal, #new-material-modal').modal('hide');
        $('.ui.dimmer:first .loader')
            .text('Requesting server to add the new part, please wait...');
        $('.ui.dimmer:first').dimmer('show');
        $.post('/api/part', {
            data: JSON.stringify(data),
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success === true)
                $('.ui.dimmer:first .loader')
                .text('Success, closing...');
            else
                $('.ui.dimmer:first .loader')
                .text('Failed, closing...');
            setTimeout(() => {
                $('.ui.dimmer:first').dimmer('hide');
            }, 1000);
        });
    });


function createPngDownload(fileName, canvas) {
    let aLink = $('<a></a>');
    aLink
        .attr('download', fileName)
        .attr('href', canvas.toDataURL('image/png'));
    aLink[0].click();
}

$('#save-button')
    .on('click', function () {});

$('#image-button').on('click', function () {
    html2canvas($('#canvas'), {
        onrendered: (canvas) => createPngDownload('design.png', canvas)
    });
});

let currentMode;
const simpleModes = {
    modifyItem: $('#drag-item'),
    dragCanvas: $('#drag-canvas'),
    deleteItem: $('#delete-item'),
    inspectItem: $('#inspect-item'),
    chassisItem: $('#chassis-item'),
};
const modes = $.extend(true, {
    addConnection: $('#connection-dropdown-button'),
    chooseInteractive: $('#interactive-button')
}, simpleModes);

let newConnectionType, newConnectionStep;
let newConnectionSource, newConnectionTarget;
let previewConnection = {};

const mode2str = {
    modifyItem: 'Drag',
    dragCanvas: 'Drag ALL',
    deleteItem: 'Delete',
    inspectItem: 'Inspect',
    chassisItem: 'Setting Chassis',
    addConnection: 'Add Connection',
    chooseInteractive: 'Chose Interactive'
};

function selectMode(mode) {
    if (currentMode === mode)
        return;
    let button = modes[currentMode];
    if (button !== undefined) {
        button.trigger('deselect');
        button.removeClass('active');
    }
    currentMode = mode;
    button = modes[mode];
    button.addClass('active');
    button.trigger('select');

    $('#bi-mode').text(mode2str[mode])
}

$('#chassis-item')
    .on('click', () => {
        selectMode('chassisItem')
    })
    .on('select', () => {
        design.unHighlightDevice($('.SDinDesign-device, .SDinDesign-part'));
        $('.SDinDesign-device').off('click');
        $('.SDinDesign-device')
            .off('mouseenter')
            .on('mouseenter', function () {
                design.highlightDevice($(this), 0.4);
            })
            .off('mouseleave')
            .on('mouseleave', function () {
                design.unHighlightDevice($(this));
            })
            .off('click')
            .on('click', function () {
                $('#set-chassis-modal').modal('show');
            });
    })
    .on('deselect', () => {
        $('.SDinDesign-device')
            .off('mouseenter')
            .off('mouseleave')
            .off('click');

    })
    .popup({
        content: 'Select the device and change its chassis.'
    })

$('#drag-item')
    .on('click', () => {
        selectMode('modifyItem');
    })
    .popup({
        content: 'Drag and move devices and parts.'
    });
$('#drag-canvas')
    .on('click', () => {
        selectMode('dragCanvas');
    })
    .on('select', () => {
        $(this._canvas).css({
            cursor: 'pointer'
        });
        $('.SDinDesign-part, .SDinDesign-device').css({
            pointerEvents: 'none'
        });
        design.enableDrag();
    })
    .on('deselect', () => {
        $(this._canvas).css({
            cursor: ''
        });
        $('.SDinDesign-part, .SDinDesign-device').css({
            pointerEvents: ''
        });
        design.disableDrag();
    })
    .popup({
        content: 'Drag and move canvas.'
    });
$('#inspect-item')
    .on('click', () => {
        selectMode('inspectItem');
    })
    .on('select', () => {
        design.unHighlightDevice($('.SDinDesign-device, .SDinDesign-part'));
        $('.SDinDesign-device').off('click');
        $('.SDinDesign-part')
            .off('mouseenter')
            .on('mouseenter', function () {
                design.highlightDevice($(this), 0.4);
            })
            .off('mouseleave')
            .on('mouseleave', function () {
                design.unHighlightDevice($(this));
            })
            .off('click')
            .on('click', function () {
                let data = design.getData(this);
                console.log(data);
                let itemModal = $('#inspect-item-modal');
                itemModal.modal('show');
                // TODO: type and role is (incorrectly) the same here.
                // change it when "type and role" is fixed.
                itemModal
                    .find('input[name=component-role]')
                    .val(data['part']['type']);
                itemModal
                    .find('input[name=component-id]')
                    .val(data['part']['name']);
                itemModal
                    .find('input[name=component-name]')
                    .val(data['part']['name']);
                itemModal
                    .find('textarea[name=component-description]')
                    .val(data['part']['description']);
                $.ajax('/api/plasm_part', {
                    data: {
                        name: data['part']['name']
                    },
                    success: (data) => {
                        console.log(data);
                        itemModal
                            .find('textarea[name=component-sequence]')
                            .val(data['seq']);
                    }
                });
            });
    })
    .on('deselect', () => {
        $('.SDinDesign-device, #canvas>.SDinDesign-part')
            .off('click')
            .on('click', function () {
                SDinDesign.preventClickOnDrag(design, $(this));
            });
        $('.SDinDesign-device>.SDinDesign-part')
            .off('mouseenter')
            .off('mouseleave')
            .off('click');
        design.unHighlightDevice($('.SDinDesign-part, .SDinDesign-device'));
    })
    .popup({
        content: 'Inspect Item'
    });
$('#connection-dropdown')
    .dropdown({
        onChange: (value) => {
            newConnectionType = value;
        }
    });
$('#connection-dropdown-button')
    .on('click', () => {
        selectMode('addConnection');
        newConnectionType = 'stimulation';
    })
    .on('select', () => {
        console.log('Begin adding new connection.');
        newConnectionStep = 'chooseSource';
        design.unHighlightDevice($('.SDinDesign-device, .SDinDesign-part'));
        $('.SDinDesign-device').off('click');
        $('.SDinDesign-part')
            .off('mouseenter')
            .on('mouseenter', function () {
                if ($(this).data('connectionSelected') !== true) {
                    design.highlightDevice($(this), 0.4);
                    if (newConnectionStep === 'chooseTarget' && newConnectionType !== 'delete') {
                        previewConnection = {
                            start: newConnectionSource,
                            end: $(this).attr('part-cid'),
                            type: newConnectionType
                        };
                        design.addLink(previewConnection, true);
                        design.redrawDesign();
                    }
                }
            })
            .off('mouseleave')
            .on('mouseleave', function () {
                if ($(this).data('connectionSelected') !== true) {
                    design.unHighlightDevice($(this));
                    if (previewConnection !== undefined) {
                        design.removeLink(previewConnection);
                        previewConnection = undefined;
                    }
                }
            })
            .off('click')
            .on('click', function () {
                if ($(this).data('connectionSelected') !== true) {
                    design.highlightDevice($(this), 0.8);
                    $(this).data('connectionSelected', true);
                    if (newConnectionStep === 'chooseSource') {
                        newConnectionSource = $(this).attr('part-cid');
                        console.log(`Choose start: ${newConnectionSource}`);
                        newConnectionStep = 'chooseTarget';
                    } else if (newConnectionStep === 'chooseTarget') {
                        newConnectionTarget = $(this).attr('part-cid');
                        console.log(`Choose end: ${newConnectionTarget}`);
                        newConnectionStep = 'finished';
                        finishNewConnection();
                    }
                } else {
                    design.unHighlightDevice($(this));
                    $(this).data('connectionSelected', false);
                    if (newConnectionStep === 'chooseTarget') {
                        newConnectionStep = 'chooseSource';
                        newConnectionSource = undefined;
                    }
                }
            });
    })
    .on('deselect', () => {
        $('.SDinDesign-device, #canvas>.SDinDesign-part')
            .off('click')
            .on('click', function () {
                SDinDesign.preventClickOnDrag(design, $(this));
            });
        $('.SDinDesign-device>.SDinDesign-part')
            .off('mouseenter')
            .off('mouseleave')
            .off('click');
        design.unHighlightDevice($('.SDinDesign-part, .SDinDesign-device'));
        $('.SDinDesign-part, .SDinDesign-device').data('connectionSelected', false);
    })
    .popup({
        content: 'Add or remove a connection.'
    });

function finishNewConnection() {
    if (newConnectionType === 'delete')
        design.recordHistory(`Delete connection [${newConnectionSource}, ${newConnectionTarget}].`);
    else
        design.recordHistory(`New ${newConnectionType} connection [${newConnectionSource}, ${newConnectionTarget}].`);
    let data = {
        start: parseInt(newConnectionSource, 10),
        end: parseInt(newConnectionTarget),
        type: newConnectionType
    };
    if (newConnectionType === 'delete') {
        let removingIndex;
        $.each(design._design.lines, (index, value) => {
            if (value.start === data.start && value.end === data.end)
                removingIndex = index;
        });
        design.removeLink(design._design.lines[removingIndex]);
        design._design.lines.splice(removingIndex, 1);
    } else {
        design._design.lines.push(data);
        design.addLink(data, false);
    }
    if (previewConnection !== undefined) {
        design.removeLink(previewConnection);
        previewConnection = undefined;
    }
    design.redrawDesign();
    selectMode('modifyItem');
}
let currentPopupId;
$('#interactive-button')
    .on('click', () => {
        selectMode('chooseInteractive');
    })
    .on('select', () => {
        design.unHighlightDevice($('.SDinDesign-device, .SDinDesign-part'));
        $('.SDinDesign-device').off('click');
        $('.SDinDesign-part')
            .off('mouseenter')
            .on('mouseenter', function () {
                design.highlightDevice($(this), 0.4);
            })
            .off('mouseleave')
            .on('mouseleave', function () {
                design.unHighlightDevice($(this));
            })
            .off('click')
            .on('click', function () {
                let id = $(this).attr('part-id');
                if (currentPopupId === id)
                    return;
                currentPopupId = id;
                $('.SDinDesign-part').popup('destroy');
                $('.ui.dimmer:first .loader')
                    .text('Loading interact data...');
                $('.ui.dimmer:first').dimmer('show');
                $.get(`/api/interact?id=${id}`, (value) => {
                    let table = $('<div></div>')
                        .append('<h5 class="ui header">Predicted interaction</h5>')
                        .append('<table></table>')
                        .css({
                            maxHeight: 600,
                            overflowY: 'auto'
                        });
                    table.children('table')
                        .addClass('ui basic compact striped table')
                        .append('<tr><th>BBa</th><th>Name</th><th>Score</th><th>Type</th></tr>');

                    // convert parts to table
                    let rows = [];
                    $.each(value.parts, (i, v) => {
                        if (i > 10)
                            return;
                        if (v.score < 0)
                            return;
                        let row = $(`<tr><td>${v.BBa}</td><td>${v.name}</td><td>${v.score}</td><td>${v.type}</td></tr>`);
                        row.attr('part-id', v.id);
                        row.appendTo(table.children('table'));
                        rows.push(row);
                    });

                    $('.ui.dimmer:first').dimmer('hide');
                    $(this).popup({
                        variation: 'flowing',
                        on: 'click',
                        html: table.html()
                    });
                    $(this).popup('show');

                    $('.popup tr').each((i, row) => {
                        if (i == 0)
                            return;
                        $(row).on('mouseenter', function () {
                            setPartPanel($(this).attr('part-id'));
                        }).css({
                            cursor: 'pointer'
                        });
                    });
                });
            });
    })
    .on('deselect', () => {
        $(`[part-id=${currentPopupId}]`).popup('destroy');
        $('.SDinDesign-device, #canvas>.SDinDesign-part')
            .off('click')
            .on('click', function () {
                SDinDesign.preventClickOnDrag(design, $(this));
            });
        $('.SDinDesign-device>.SDinDesign-part')
            .off('mouseenter')
            .off('mouseleave')
            .off('click');
        design.unHighlightDevice($('.SDinDesign-part, .SDinDesign-device'));
    })
    .popup({
        variation: 'flowing popup',
        content: 'Check predicted interactions of parts.'
    });

//let tmp;

$('#delete-item')
    .on('click', () => {
        selectMode('deleteItem');
    })
    .on('select', () => {
        design.unHighlightDevice($('.SDinDesign-device, .SDinDesign-part'));
        $('.SDinDesign-device').off('click');
        $('.SDinDesign-part')
            .off('mouseenter')
            .on('mouseenter', function () {
                design.highlightDevice($(this), 0.4);
            })
            .off('mouseleave')
            .on('mouseleave', function () {
                design.unHighlightDevice($(this));
            })
            .off('click')
            .on('click', function () {
                let data = design.getData(this);
                console.log(data);
                if (data.part !== undefined)
                    design.deletePart(data.device, data.part);
            });
    })
    .on('deselect', () => {
        $('.SDinDesign-device, #canvas>.SDinDesign-part')
            .off('click')
            .on('click', function () {
                SDinDesign.preventClickOnDrag(design, $(this));
            });
        $('.SDinDesign-device>.SDinDesign-part')
            .off('mouseenter')
            .off('mouseleave')
            .off('click');
        design.unHighlightDevice($('.SDinDesign-part, .SDinDesign-device'));
    })
    .popup({
        variation: 'flowing popup',
        content: 'Delete a part.'
    });

$('#clear-all-button')
    .on('click', () => {
        $('#clear-all-modal').modal('show');
    })
    .popup({
        content: 'CLEAR THE CANVAS!'
    });


$('#real-clear-all-button')
    .on('click', () => {
        design.clearAll();
        $('#chassis-dropdown').dropdown(
            'set selected', 'Escherichia Coli'
        );
    });

//TODO: only this place use Chart.js
// Consider to remove Chart.js
// Use new chart js code: echart.js to implement the stimulate
$('#simulation-button')
    .on('click', () => {
        let data = design.matrix;
        let postData = {
            data: JSON.stringify(data.matrix),
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        };
        $('.ui.dimmer:first .loader')
            .text('Running on server, please wait...');
        $('.ui.dimmer:first').dimmer('show');
        $.post('/api/simulation', postData, (v) => {
            $('.ui.dimmer:first').dimmer('hide');
            $('#simulation-modal').modal('show');
            let labels = v.time;
            let datasets = [];
            for (let i = 0; i < v.result[0].length; ++i)
                datasets.push({
                    label: data.partName[i],
                    data: [],
                    fill: false,
                    pointRadius: 0,
                    borderColor: `hsl(${i * 360 / v.result[0].length}, 100%, 80%)`,
                    backgroundColor: 'rgba(0, 0, 0, 0)'
                });
            v.result.forEach((d) => {
                d.forEach((x, i) => {
                    datasets[i].data.push(x * 38);
                });
            });
            new Chart($('#simulation-result'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    scales: {
                        xAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: (v) => v.toFixed(1)
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'time (h)'
                            }
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'concentration (μM)'
                            }
                        }]
                    }
                }
            });
        });
    })
    .popup({
        content: 'Run simulation on the design.'
    });


// Chassis dropdown set
$('#chassis-dropdown').dropdown(
    (function () {
        let ret = {
            values: []
        }
        CHASSIS.forEach(function (element) {
            ret.values.push({
                name: element,
                value: element,
            })
        })
        ret.values[0].selected = true;
        ret.onChange = function (value) {
            design.setChassis(value)
        }
        return ret;
    })()
).popup({
    content: 'Choose your chassis.'
});

$('#set-chassis-button').on('click', () => {
    $('#set-chassis-modal').modal('hide');
})


$('#show-plasmid').on('click', function () {
    $('#plasmid-modal').modal('show');
});

$(window)
    .on('keydown', (event) => {
        if (event.ctrlKey === true) selectMode('dragCanvas');
    })
    .on('keyup', () => {
        selectMode('modifyItem');
    });

selectMode('modifyItem');

$('#realtime-enter')
    .on('click', function() {
        console.log('click realtime enter button');
        if (design.design.id == -1) {
            if ($('#info-box-not-saved-msg').length > 0) {
                return;
            }
            let error_msg = `
            <b>
                <li id="info-box-not-saved-msg" class="orad-error"> 
                    Please save your design before entering magic realtime space!
                </li>
            </b>
            `;
            let $error_msg = $(error_msg)
            $('#info-box ul').prepend($error_msg);
            setTimeout(() => {
                $('#info-box-not-saved-msg').remove();
            }, 5000);
            return;
        }

        $.post({
            url: `/api/realtime/${design.design.id}`,
            data: {
                'design_data': JSON.stringify(design.design),
                'first_time': JSON.stringify(true),
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            }
        });

        // below codes just INSERT 'realtime' at the LAST SECOND position.
        // eg /design/1667 to /design/realtime/1667
        let pn = window.location.pathname.split('/');
        pn.splice(pn.length-1, 0, 'realtime');
        window.location.pathname = pn.join('/');
    })
    .popup({
        content: 'Click to go into realtime mode'
    });


let bi_user_text = $('#bi-user').text()
$('#bi-user').text(bi_user_text.replace('{}', authorname));

$('#info-box').on('mouseover', function() {
    //$(this).css('background', 'rgba(255, 255, 255, 0.3');
    $(this).css('opacity', '0.2');
}).on('mouseleave', function() {
    $(this).css('opacity', '0.8');
});