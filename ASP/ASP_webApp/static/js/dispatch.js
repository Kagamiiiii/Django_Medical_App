
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
        url: "./dispatchDetail/",
        success: function (respond) {
            $('#maincontent').html(respond);
            $('#maincontent').css("display", "block");
            $('#downloadItineraryButton').css("display", "inline-block");
            $('#updateToDispatchButton').css("display", "inline-block");
        }
      }
    );
}

function downloadItinerary(){
    $('#updateToDispatch').prop("disabled", false);
}

function updateToDispatch(){
    // restore all states of your html element. refresh the page.
    return null;
}
