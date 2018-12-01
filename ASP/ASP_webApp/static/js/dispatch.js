var items = null;

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
            $('#maincontent').show();
            $('#downloadItineraryButton').css("display", "inline-block");
            $('#updateToDispatchButton').css("display", "inline-block");
            $.ajax({
                  type: "POST",
                  url: "./dispatchDetailJson/",
                  success: function (respond) {
                      window.items = respond;
                  }
                }
            );
        }
      }
    );
}

function downloadItinerary(){
    $('#updateToDispatchButton').prop("disabled", false);
    location.replace('./getItinerary/');
}

function updateToDispatch(){
    // restore all states of your html element. refresh the page.
    $.ajax({
          type: "POST",
          url: "./dispatchUpdate/",
          data: {
            item: window.items,
          },
          traditional: true,
          success: function (respond) {
              alert("Dispatch updated!");
              $.ajax({
                  type: "POST",
                  url: "./sendEmail/",
                  success: function (respond) {
                      window.location.reload(true);
                  }
              });
          }
        }
    );

}