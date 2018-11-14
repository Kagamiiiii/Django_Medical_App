function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function requestCategory(){

var csrftoken = Cookies.get('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var e = document.getElementById("selector-inner");
var strUser = e.options[e.selectedIndex].text;

$.ajax({
      type: "POST",
      url: "./displayByCategory/",
      data: {
        category : strUser
      },
      dataType: 'json',
      success: function (respond) {
          // clear all element in maincontent first.
          alert('msg');
      }
    });
};