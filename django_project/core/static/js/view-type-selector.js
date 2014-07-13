$(document).ready(function () {
    var viewSelected = getCookie('view_type');
    if (viewSelected==='full') {
        $('#slim-view-selected').css('display', 'none');
    } else {
        $('#full-view-selected').css('display', 'none');
    };
    $('#select-slim').click(function(){
        setCookie('view_type', 'slim', 14)
        location.reload()
    });

    $('#select-full').click(function(){
        setCookie('view_type', 'full', 14)
        location.reload()
    });
    
});