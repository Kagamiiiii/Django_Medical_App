var items = null;
var cart = [];
var priority = "Low";
var total_weight = 0;


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
  if (strUser != "Please select a category...") {
    $.ajax({
          type: "POST",
          url: "./displayByCategory/",
          data: {
            category : strUser
          },
          success: function (respond) {
              $('#maincontent').html(respond);
              $('#maincontent').show();
              $.ajax({
                    type: "POST",
                    url: "./displayByCategoryJson/",
                    data: {
                      category : strUser
                    },
                    success: function (respond) {
                      window.items = respond;
                  }
                }
              );
          }
        }
      );
    } else {
      $('#maincontent').hide();
    }
}

function orderCreated(){
  items = null;
  cart = [];
  priority = "Low";
  updateWeight();
  updateCart();
  $('#success-message').css({
        opacity: 0,
        display: 'inline-block'
    }).animate({opacity:1},1500,function() {
      $('#success-message').animate({opacity:0},1500,function() {
        $('#success-message').css({
              opacity: 1,
              display: 'none'
          });
        })
    });
  }

function createOrder(){
  var e = document.getElementById("priority-selector-inner");
  var selected_priority = e.options[e.selectedIndex].text;
  if (selected_priority == "Select priority") {
    alert("Please select a priority!");
  } else {
    let order = {
        priority: selected_priority,
        cart: cart,
        weight: total_weight,
        // clinic_id: 1,
        // account_id: 1
      };
    $.ajax({
          type: "POST",
          url: "./createOrder/",
          data: {
            order: JSON.stringify(order),
          },
          success: function (respond) {
            orderCreated();
        }
    });
  }

}

function strip(num, precision = 4) {
  return +parseFloat(num.toPrecision(precision));
}

function updateWeight(){
    total_weight = 0;
    for (item in cart){
      total_weight += cart[item].quantity * cart[item].weight;
    }
    $('#weight').text(strip(total_weight));
    if( $('#weight').text() >= 25){
      $('#weight-warning').show();
      $('#createOrder').prop('disabled', true);
    } else {
      $('#weight-warning').hide();
      $('#createOrder').prop('disabled', false);
    }
}

function updateCart() {
  if (cart.length == 0) {
    $('.cart-body').remove();
    $('.card-title').show();
    $('.card-body').css("padding", "20px");
    $('#createOrder').prop('disabled', true);
    return;
  }
  $('.card-title').hide();
  if ( $('.cart-body').length ){
    $('.cart-body').remove();
  }
  $('.card-body').css("padding", "0px");
  $('.card-body').append("<div class=\"cart-body\">");
  $('.cart-body').append("<ul class=\"list-group\">");
  for (let i = 0; i < cart.length; i++) {
    var string = "<li class=\"list-group-item\"> <b>Name</b>: " +
    cart[i].name + "<br> <b>Quantity</b>: " + cart[i].quantity + "<br>  <b>Weight</b>: " + cart[i].weight + "</li>";
    $('.cart-body').append(string);
  }
  $('.cart-body').append("</ul>");
  $('.card-body').append("</div>");
  $('#createOrder').prop('disabled', false);
}

function changePriority(){

  var e = document.getElementById("priority-selector-inner");
  var selected_priority = e.options[e.selectedIndex].text;
  if (selected_priority != "Select priority") {
    priority = selected_priority;
  }
}

function checkboxToggle(element){
    if ($(element).prop("checked") == true) {
        var quantity = parseInt($(element).parent().siblings('.category_quantity_parent').children()[0].value);
        var id = $(element).parent().siblings('.category_id_parent').html();
        var weight = 0;
        var name = "";
        var item;
        for ( item in window.items ){
          if (items[item].id == id){
              weight = items[item].weight;
              name = items[item].name;
          }
        }
        let cart_item = {
            item_id: parseInt(id),
            name: name,
            quantity: quantity,
            weight: weight,
        };
        cart.push(cart_item);
        updateCart()
        updateWeight();
    } else {
        var id = $(element).parent().siblings('.category_id_parent').html();
        for (let i = 0; i < cart.length; i++) {
            if (cart[i].item_id == id) {
                cart.splice(i, 1);
            }
        }
        updateCart()
        updateWeight();
    }
}

function toggleBrowseSupplies(){
    $('#bs-section-button').addClass("active");
    $('#vo-section-button').removeClass( "active" );
    $('#bs-section').show();
    $('#vo-section').hide();
}

function toggleViewOrder(){
    var csrftoken = Cookies.get('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#bs-section-button').removeClass("active");
    $('#vo-section-button').addClass("active");

    $('#bs-section').hide();


    $.ajax({
          type: "POST",
          url: "./viewOrder/",
          data: {
            account_id : 1,
          },
          success: function (respond) {
            // console.log("success!!");
              $('#vo-section').html(respond);
              $('#vo-section').show();
          }
        }
      );
}

function toggleCheckbox(element){
    var content = parseInt($(element).val());
    if ( content > 0) {
      $(element).parent().siblings('#checkbox').children().removeAttr("disabled");
    } else {
      $(element).parent().siblings('#checkbox').children().prop("disabled", true);
    }
}

function viewOrderAction(element){
    var id = $(element).parent().siblings("#order_id").html();
    var status = $(element).parent().siblings("#status").html();
    $.ajax({
          type: "POST",
          url: "./orderAction/",
          data: {
            orderID: id,
          },
          success: function (respond) {
            if ( status == "Queued for Processing"){
                $(element).prop('disabled', true);
                $(element).parent().siblings("#status").html("Cancelled");
                alert("Order cancelled!");
            } else {
                $(element).prop('disabled', true);
                $(element).parent().siblings("#status").html("Delivered");
                alert("Order delivered!");
            }
          }
        }
    );
}
