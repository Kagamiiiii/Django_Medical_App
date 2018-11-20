function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function processTop(){
  var csrftoken = Cookies.get('csrftoken');

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });

  $.ajax({
    type: "POST",
    url: "./processOrder/",
    success: function (respond) {
      $('#maincontent').hide();
      $('#alt-maincontent').show();
      $('#alt-maincontent').html(respond);
    }
  });
}

function obtainSL(){
  $("completeOrderButton").prop("disabled", false);
  location.replace('./PDF/');
}

function completeOrder(){
  $.ajax({
    type: "POST",
    url: "./updateStatus/",
    success: function (respond) {
      alert("Order Completed!");
    }
  });
}
