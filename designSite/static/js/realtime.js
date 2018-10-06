/* global design */
/* eslint-disable no-console */
/* exported my_syn */
let isRealtimeReading = true;
let $bi_user_read = $('#bi-user-read');
let $bi_user_write = $('#bi-user-write');

$bi_user_write.hide();

$('#canvas').css('background', 'rgba(248, 231, 233, 0.7)');
$('#realtime-button')
.on('click', function() {
    isRealtimeReading = !isRealtimeReading;
    if (isRealtimeReading) {
        $('#canvas').css('background', 'rgba(248, 231, 233, 0.7)');

        //for live canvas
        $('#live-canvas').removeClass('draw');
        $('#live-canvas').removeClass('erase');
        unloadLiveCanvasDraw();
        initLiveCanvasShow();

        $bi_user_read.toggle();
        $bi_user_write.toggle();
    } else {
        $('#canvas').css('background', '');

        //for live canvas
            $('#live-canvas').addClass('draw');
            unloadLiveCanvasShow()
            initLiveCanvasDraw();
        }
        $bi_user_read.toggle();
        $bi_user_write.toggle();
    })
    .popup({
        content: 'click me to toggle following or not.'
    });
// $('#realtime-save')
//     .on('click', function() {
//         $.post({
//             url: `/api/realtime/${design.design.id}`,
//             data: {
//                 'design_data': JSON.stringify(design.design),
//                 'first_time': JSON.stringify(false),
//                 csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
//             },
//             success: () => {
//                 console.log('success');
//             }
//         });
//     })
//     .popup({
//         content: 'click me to send your changes to others.'
//     });

setInterval(() => {
    if (isRealtimeReading) {
        $.get({
            'url': `/api/realtime/${design.design.id}`,
            success: (data) => {
                let design_data = JSON.parse(data['design_data']);
                design.design = design_data;

                __protocol_refresh_from_design();
            }
        });
    } else {
        $.post({
            url: `/api/realtime/${design.design.id}`,
            data: {
                'design_data': JSON.stringify(design.design),
                'first_time': JSON.stringify(false),
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
        });
    }
}, 500);

// function my_syn() {
//     $.post({
//         url: `/api/realtime/${design.design.id}`,
//         data: {
//             'design_data': JSON.stringify(design.design),
//             'first_time': JSON.stringify(false),
//             csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
//         },
//     });
// }
$('#realtime-exit')
    .on('click', function() {
        let pn = window.location.pathname.split('/');
        pn.splice(pn.length-2, 1); // remove second to last
        window.location.pathname = pn.join('/');
        
        //for live canvas

        unloadLiveCanvasDraw();
        unloadLiveCanvasShow()
        $('#live-canvas').addClass('hidden');
    })
    .popup({
        content: 'exit real time share.'
    });