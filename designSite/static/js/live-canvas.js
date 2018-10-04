var cvs = $('#live-canvas')[0].getContext('2d');

var penWeight = 1;
var eraseWeight = 14;
var penColor = '#f00';
var posList = [];
var renderList = [];
var rendering = [];
var renderingType = 'draw';
var curOrder = 0;
var fetchRenderListInt = undefined;
var renderInt = undefined;
var onErase = false;


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
function drawOnCanvas(e) {
    var move_x = e.clientX - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
    var move_y = e.clientY - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

    var info_x = e.clientX - $('#info-box')[0].offsetLeft + document.body.scrollLeft;
    var info_y = e.clientY - $('#info-box')[0].offsetTop + document.body.scrollTop;

    if (info_x >= 0 && info_x <= $('#info-box').outerWidth() && info_y > 0 && info_y <= $('#info-box').outerHeight()) {
        $('#info-box').css({ 'opacity': '0.2' });
    } else {
        $('#info-box').css({ 'opacity': '0.8' });
    }

    posList.push([move_x, move_y]);
    if (onErase) {
        cvs.clearRect(move_x, move_y, eraseWeight, eraseWeight);
    } else {
        cvs.lineTo(move_x, move_y);
        cvs.stroke();
    }
}

function finishDraw(e) {
    if (onErase) {
        $('.SDinDesign-part').removeClass('erase');
        $('.SDinDesign-device').removeClass('erase');
    } else {
        $('.SDinDesign-part').removeClass('draw');
        $('.SDinDesign-device').removeClass('draw');
    }
    $('#info-box').css({ 'opacity': '0.8' });
    cvs.closePath();

    console.log(posList);
    if (onErase) {
        curDrawType = 'erase';
    } else {
        curDrawType = 'draw';
    }

    $.post({
        url: `/api/liveCanvas/${design.design.id}/`,
        data: {
            'path': JSON.stringify(posList),
            'type': curDrawType,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
    });
    posList = [];

    $('#live-canvas').unbind("mousemove mouseup");
    $('.SDinDesign-part').unbind("mousemove mouseup");
    $('.SDinDesign-device').unbind("mousemove mouseup");
}

function initLiveCanvasDraw() {
    onErase = false;
    $('#live-canvas').mousedown(function (e) {
        if (onErase) {
            $('.SDinDesign-part').addClass('erase');
            $('.SDinDesign-device').addClass('erase');
        } else {
            $('.SDinDesign-part').addClass('draw');
            $('.SDinDesign-device').addClass('draw');
        }
        var start_x = e.clientX - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
        var start_y = e.clientY - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

        if (start_y < 60) return;
        posList.push([start_x, start_y]);
        if (onErase) {
            cvs.clearRect(start_x, start_y, eraseWeight, eraseWeight);
        } else {
            cvs.beginPath();

            cvs.moveTo(start_x, start_y);

            cvs.lineCap = 'round';
            cvs.lineJoin = "round";
            cvs.strokeStyle = penColor;
            cvs.lineWidth = penWeight;
        }
        
        $('.SDinDesign-device').mousemove(function (e) {
            drawOnCanvas(e);
        });
        $('.SDinDesign-part').mousemove(function (e) {
            drawOnCanvas(e);
        });
        $('#live-canvas').mousemove(function (e) {
            drawOnCanvas(e);
        });

        $('.SDinDesign-device').mouseup(function (e) {
            finishDraw(e);
        });
        $('.SDinDesign-part').mouseup(function (e) {
            finishDraw(e);
        });
        $('#live-canvas').mouseup(function (e) {
            finishDraw(e);
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
            } else {
                pos = rendering.shift();
                var start_x = pos[0] - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
                var start_y = pos[1] - $('#live-canvas')[0].offsetTop + document.body.scrollTop;

                if (renderingType === 'draw'){

                    cvs.beginPath();
                    cvs.moveTo(start_x, start_y);

                    cvs.lineCap = 'round';
                    cvs.lineJoin = "round";
                    cvs.strokeStyle = penColor;
                    cvs.lineWidth = penWeight;

                    if (renderList.length === 0) {
                        cvs.closePath();
                    }

                } else if (renderingType === 'erase') {
                    cvs.clearRect(start_x, start_y, eraseWeight, eraseWeight);
                }
            }
        }
    } else {
        pos = rendering.shift();
        var move_x = pos[0] - $('#live-canvas')[0].offsetLeft + document.body.scrollLeft;
        var move_y = pos[1] - $('#live-canvas')[0].offsetTop + document.body.scrollTop;
        if (renderingType === 'draw') {
            cvs.lineTo(move_x, move_y);

            cvs.stroke();
            if (rendering.length === 0) {
                cvs.closePath();
            }
        } else if (renderingType === 'erase') {
            cvs.clearRect(move_x, move_y, eraseWeight, eraseWeight);
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
                if (curOrder - tempOrder > 5) {
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
    .on('click', function () {
        onErase = false;
        $('#live-canvas').removeClass('erase');
        $('#live-canvas').addClass('draw');
    })
    .popup({
        content: 'draw lines on live canvas.'
    });
$('#live-canvas-erase')
    .on('click', function () {
        onErase = true;
        $('#live-canvas').removeClass('draw');
        $('#live-canvas').addClass('erase');
    })
    .popup({
        content: 'erase lines on live canvas.'
    });
//on viewer page
$('#live-canvas').removeClass('hidden');
initLiveCanvasShow();