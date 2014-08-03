$(document).ready(function() {
    // hide the download button from mobile/tablet devices
    if (typeof window.orientation == 'undefined') {
        // pass
    } else {
        var hiddenOnMobile = document.getElementsByClassName("display-none-mobile");
        for (i = 0; i < hiddenOnMobile.length; ++i) {
            $(hiddenOnMobile[i]).css('display', 'none');
        }
    };
});