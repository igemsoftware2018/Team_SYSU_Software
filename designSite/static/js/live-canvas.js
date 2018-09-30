var cvs = $('#live-canvas')[0].getContext('2d');

var penWeight = 1;
var penColor = '#f00';
var posList = [];
var renderList = [];
var rendering = [];
var renderingType = 'draw';
var curOrder = 0;
var fetchRenderListInt = undefined;
var renderInt = undefined;


// auto resize
$(window).resize(resizeCanvas);
function resizeCanvas() {
    //unloadLiveCanvasShow();
    $('#live-canvas').attr("width", $(window).get(0).innerWidth);
    $('#live-canvas').attr("height", $(window).get(0).innerHeight);
    renderList = []
    rendering = []
    renderingType = 'draw';
    curOrder = 0;
    //initLiveCanvasShow();
};
resizeCanvas();

function initLiveCanvasDraw() {
    

    $('#live-canvas').mousedown(function (e) {
        var start_x = e.clientX - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
        var start_y = e.clientY - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

        if (start_y < 60) return;
        cvs.beginPath();

        cvs.moveTo(start_x, start_y);

        posList.push([start_x, start_y]);

        cvs.lineCap = 'round';
        cvs.lineJoin = "round";
        cvs.strokeStyle = penColor;
        cvs.lineWidth = penWeight;


        $('#live-canvas').mousemove(function (e) {

            var move_x = e.clientX - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
            var move_y = e.clientY - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

            cvs.lineTo(move_x, move_y);	
            posList.push([move_x, move_y]);

            cvs.stroke();
        });


        $('#live-canvas').mouseup(function (e) {

            cvs.closePath();

            console.log(posList);
            $.post({
                url: `/api/liveCanvas/${design.design.id}/`,
                data: {
                    'path': JSON.stringify(posList),
                    'type': 'draw',
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                },
            });
            posList = [];

            $('#live-canvas').unbind("mousemove mouseup");
        });
    });
}

function unloadLiveCanvasDraw() {
    $('#live-canvas').unbind("mousedown");
    posList = [];
}

function renderLiveCanvas() {
    if (rendering.length === 0) {
        if (renderList.length !== 0) {
            nextRender = renderList.shift();
            rendering = nextRender.drawPath;
            renderingType = nextRender.drawType;

            if (renderingType === 'clear') {
                // 清空画布
                cvs.clearRect(0, 0, $(window).get(0).innerWidth, $(window).get(0).innerHeight);
                return;
            }

            pos = rendering.shift();

            var start_x = pos[0] - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
            var start_y = pos[1] - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

            cvs.beginPath();

            cvs.moveTo(start_x, start_y);

            cvs.lineCap = 'round';
            cvs.lineJoin = "round";
            cvs.strokeStyle = penColor;
            cvs.lineWidth = penWeight;
            if (renderList.length === 0) {
                cvs.closePath();
            }
        }
    } else {
        pos = rendering.shift();
        var move_x = pos[0] - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
        var move_y = pos[1] - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

        cvs.lineTo(move_x, move_y);

        cvs.stroke();
        if (rendering.length === 0) {
            cvs.closePath();
        }
    }
}


function initLiveCanvasShow() {
    // 可能可以和实时演示轮询合并

    fetchRenderListInt = setInterval(() => {
        $.get({
            'url': `/api/liveCanvas/${design.design.id}/?Order=` + curOrder,
            success: (data) => {
                if (data['latestOrder'] === 'latest') return;
                fetchRenderList = data['drawList'];
                tempOrder = curOrder;
                curOrder = data['latestOrder'];
                if (fetchRenderList.length !== 0)
                    renderList = renderList.concat(fetchRenderList);
                if (tempOrder === 0) {
                    while (renderList.length !== 0) {
                        try {
                            renderLiveCanvas();
                        } catch(e) {}
                    }
                } else {
                    renderInt = setInterval(renderLiveCanvas, 30);
                }
            }
        });
    }, 500);
    
}

function unloadLiveCanvasShow() {
    clearInterval(fetchRenderListInt);
    clearInterval(renderInt);
}


//bind buttons
$('#live-canvas-show')
    .on('click', function () {
        if ($('#live-canvas').hasClass('hidden')) {
            $('#live-canvas').removeClass('hidden')
        } else {
            $('#live-canvas').addClass('hidden')
        }
    })
    .popup({
        content: 'show or hide live canvas.'
    });
$('#live-canvas-clear')
    .on('click', function () {
        $.post({
            url: `/api/liveCanvas/${design.design.id}/`,
            data: {
                'path': JSON.stringify([]),
                'type': 'clear',
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
        });
        cvs.clearRect(0, 0, $(window).get(0).innerWidth, $(window).get(0).innerHeight);
    })
    .popup({
        content: 'clear live canvas.'
    });
$('#live-canvas-pen')
    .popup({
        content: 'draw lines on live canvas.'
    });
$('#live-canvas-erase')
    .popup({
        content: 'erase lines on live canvas.'
    });
//on viewer page
$('#live-canvas').removeClass('hidden');
initLiveCanvasShow();