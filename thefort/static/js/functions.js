jQuery( document ).ready(function() {

    $(window).scroll(function(){
    $('.topnav').toggleClass('scrollednav py-0', $(this).scrollTop() > 50);
    });

    $('[data-toggle="tooltip"]').tooltip();
});


jQuery( document ).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();
});
