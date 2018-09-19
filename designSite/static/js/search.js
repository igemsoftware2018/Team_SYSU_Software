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
              <img src="${item.Award}" class="ui tiny bordered rounded image">
            </div>
            <p>${item.Summary}</p>
          </div>
        </div>
      </div>`);
  });

  $('.head label').on('click', function () {
    let detail = {
      'Title': "E.colipse-Who's your pABA:intelligent sun protection",
      'Team': 'ETH_Zurich',
      'Year': '2017',
      'Award': '/static/img/design/unknown.png',
      'Summary': 'to detect hazardous levels of sun radiation ...',
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
      'Description': 'to detect hazardous levels of sun radiation ...',
      'Pic3': '/static/img/design/unknown.png'
    };
    $('#item-segment').removeClass('invisible').addClass('visible');
    $('#content-segment').removeClass('visible').addClass('invisible');
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