
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function requestDispatch(){
  var csrftoken = Cookies.get('csrftoken');

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });

  $('#dispatchButton').hide();
  $('#maincontent').hide();
  $.ajax({
        type: "POST",
        url: "./dispatchView/",
        success: function (respond) {
            $('#maincontent').html(respond);
            $('#maincontent').css("display", "block");
            $('#downloadItinerary').css("display", "inline-block");
            $('#updateToDispatch').css("display", "inline-block");
        }
      }
    );
}

function updateToDispatch(){
    return null;
}

function downloadItinerary(){
    $('#updateToDispatch').prop("display", "inline-block");
}
