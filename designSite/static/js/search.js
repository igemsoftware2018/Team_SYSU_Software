window.onload = function(){
  $('.ui.dropdown').dropdown();
};

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


$('#logo').on('click', function(){
  $(location).attr('href', '/');
});
// Update some css parameters
// function updateParameters() {
//   let topBarHeight = $(".top-bar").height();
//   console.log(topBarHeight);
//   $(".top-bar p").css("font-size", String(topBarHeight * .7));
// }

// $(document).ready(function() {
//   updateParameters();
// })

// $(window).resize(updateParameters);


$('#search').on('click', function () {
  $('#content-segment').html('');
  $('#item-segment').removeClass('visible').addClass('invisible');
  $('#content-segment').removeClass('invisible').addClass('visible');
  // TODO: Change result to api result
  let result = [{
    'Title': "E.colipse-Who's your pABA:intelligent sun protection",
    'Logo': '/static/img/design/unknown.png',
    'Team': 'ETH_Zurich',
    'Year': '2017',
    'Award': '/static/img/design/unknown.png',
    'Summary': 'to detect hazardous levels of sun radiation ...'
  }, {
    'Title': "E.colipse-Who's your pABA:intelligent sun protection",
    'Logo': '/static/img/design/unknown.png',
    'Team': 'ETH_Zurich',
    'Year': '2017',
    'Award': '/static/img/design/unknown.png',
    'Summary': 'to detect hazardous levels of sun radiation ...'
  }, {
    'Title': "E.colipse-Who's your pABA:intelligent sun protection",
    'Logo': '/static/img/design/unknown.png',
    'Team': 'ETH_Zurich',
    'Year': '2017',
    'Award': '/static/img/design/unknown.png',
    'Summary': 'to detect hazardous levels of sun radiation ...'
  }];

  $.each(result, function (index, item) {
    $('#content-segment').append(
      `<div class="ui middle aligned stackable grid container">
        <div class="row head">
          <label>${item.Title}</label>
        </div>
        <div class="row">
          <div class="three wide column">
            <img src="${item.Logo}" class="ui small bordered rounded image">
          </div>
          <div class="eight wide column description">
          <div class="ui text container">
          <label class="team">Team: ${item.Team}</label>
          <label class="year">Year: ${item.Year}</label>
          <img src="${item.Award}">
          </div>
          <p>${item.Summary}</p>
          </div>
          </div>
          </div>`);
  });

  $('.head label').on('click', function () {
    $('#item-segment .ui.container').html('');
    let detail = {
      'Title': "E.colipse-Who's your pABA:intelligent sun protection",
      'Team': 'ETH_Zurich',
      'Year': '2017',
      'Award': '/static/img/design/unknown.png',
      'Summary': 'To detect hazardous levels of sum radiation, their system was based on UVR-8, a UV sensing protein' +
        'from plants and they fused UVR. To detect hazardous levels of sun radiation, their system was based on UVR-8,' +
        'a UV sensing protein from plants and they fused UVR-8.',
      'Pic1': '/static/img/design/unknown.png',
      'Pic2': '/static/img/design/unknown.png',
      'Table': [{
        'Number': 123,
        'Name': 'xxx',
        'Type': 'yyy'
      }, {
        'Number': 123,
        'Name': 'xxx',
        'Type': 'yyy'
      }, {
        'Number': 123,
        'Name': 'xxx',
        'Type': 'yyy'
      }],
      'Description': 'To detect hazardous levels of sum radiation, their system was based on UVR-8, a UV sensing protein' +
        'from plants and they fused UVR. To detect hazardous levels of sun radiation, their system was based on UVR-8,' +
        'a UV sensing protein from plants and they fused UVR-8. To detect hazardous levels of sum radiation, their system' +
        'was based on UVR-8, a UV sensing protein from plants and they fused UVR. To detect hazardous levels of sun radiation,' +
        'their system was based on UVR-8, a UV sensing protein from plants and they fused UVR-8 ...',
      'Pic3': '/static/img/design/unknown.png'
    };
    // show detail segment
    $('#item-segment').removeClass('invisible').addClass('visible');
    $('#content-segment').removeClass('visible').addClass('invisible');

    // form detail content
    let html =
      `<!-- Title -->
      <div class="head">
        <label>${detail.Title}</label>
        <i class="big icon close"></i>
      </div>

      <!-- Info -->
      <div class="ui text container">
        <label>Team: ${detail.Team}</label>
        <label>Year: ${detail.Year}</label>
        <img src="${detail.Award}">
        <p>${detail.Summary}</p>
      </div>
      <!-- Second Row -->
      <div class="second row">
        <div class="two wide column">
          <img src="${detail.Pic1}" class="ui middle bordered rounded image">
          <img src="${detail.Pic2}" class="ui middle bordered rounded image">
        </div>
        <div class="two wide column">
          <table class="ui celled table">
            <thead>
              <tr>
                <th>Number</th>
                <th>Name</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>`;

    $.each(detail.Table, (index, val) => {
      html = html +
        `<tr>
      <td data-label="Number">${val.Number}</td>
      <td data-label="Name">${val.Name}</td>
      <td data-label="Type">${val.Type}</td>
      </tr>`
    });

    html = html + `</tbody></table></div></div>
      <!-- Third Row -->
      <div class="ui container third row">
      <img src="${detail.Pic3}">
      <p>${detail.Description}</p>
      </div>`;

    $('#item-segment .ui.container').append(html);

    $('.head i').on('click', function () {
      $('#item-segment').removeClass('visible').addClass('invisible');
      $('#content-segment').removeClass('invisible').addClass('visible');
    });
  });
});

$('#design').on('click', function () {
  window.location.href = '/design';
});

$('#account').on('click', function () {
  window.location.href = '/index';
});

$('#logo').on('click', function () {
  window.location.href = '/';
});