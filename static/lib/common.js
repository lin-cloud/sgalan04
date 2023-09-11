$(document).ready(function() {
    $('.mob_menu_btn').on('click', function(e) {
        e.preventDefault();
        if (window.animatingMenu) return false;
        console.log('Hay click');
        window.animatingMenu = true;
        console.log('Vamos a animar');
        $('#menu_pop').animate({
            left: "-=100%",
        }, 300, function() {
            window.animatingMenu = false;
            console.log('Animado');
        });
    });

    $('#menu_pop_hdr a').on('click', function(e) {
        e.preventDefault();
        if (window.animatingMenu) return false;
        console.log('Hay click');
        window.animatingMenu = true;
        console.log('Vamos a animar');
        $('#menu_pop').animate({
            left: "+=100%",
        }, 300, function() {
            window.animatingMenu = false;
            console.log('Animado');
        });
    });

    $('#img_viewer a').on('click', function(e) {
        e.preventDefault();
        $('#img_viewer').animate({
            left: "+=100%",
        }, 300);
    });


});



function showImageModal(src) {
    var hi = $('#img_viewer').get(0).scrollHeight;
    var wi = $('#img_viewer').get(0).scrollWidth;
    var h = $(window).height();
    var w = $(window).width();
    console.log(wi);
    console.log(hi);

    $('#img_viewer_img').attr('src', src);
    $('#img_viewer').animate({
        left: "-=100%",
    }, 400);
$("#img_viewer_bod").children().css("height", "100%");
//$("#img_viewer_bod").children().css("width", "3000%");
}