$('.nav-link').on('click', function () {
  $('.active').removeClass('active');
  $(this).addClass('active');
});