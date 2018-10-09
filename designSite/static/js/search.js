// window.onload = function(){
//   $('.ui.dropdown').dropdown();
// };

var currentSearchType = "paper";

document.onkeydown = keyDownSearch;

function keyDownSearch(e) {
  // 兼容 FireFox, IE & Opera    
  let theEvent = e || window.event;
  let code = theEvent.keyCode || theEvent.which || theEvent.charCode;
  if (code == 13) {
    $("#search").click();
    return false;
  }
  return true;
}

$('.username').on('click', function () {
  window.location.href = '/index';
});

$('.back').add('i.chevron.left.icon')
.on('click', () => { history.back(); });

$('#design').on('click', function () {
  window.location.href = '/design';
});

$('#logo').on('click', function () {
  window.location.href = '/';
});

$(".CORADSearchSelector").on('click', function () {
  currentSearchType = $(this).attr("data-type");
  $(".CORADSearchSelector").removeClass("selected");
  $(this).addClass("selected");
})

$("#search").on("click", function () {
  window.location.href = '/search/?type=' + currentSearchType + "&keyword=" + $('#search-content').val();
})



$("img").each(function() {
  console.log($(this).attr('src'));
})