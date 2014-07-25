/* SECTION 1 */
/* setting and checking cookies */

var autoplayOn = getCookie('_autoplay');
if (autoplayOn==='true') {
    $('#autoplay-on').css('display', 'inline-block');
} else {
    $('#autoplay-off').css('display', 'inline-block');
};

$('#autoplay-on').click(function(){
    setCookie('_autoplay', 'false', 14)
    setCookie('_autoplay_continued', 'false', 14)
    $('#autoplay-on').hide();
    $('#autoplay-off').css('display', 'inline-block');
});

$('#autoplay-off').click(function(){
    setCookie('_autoplay', 'true', 14)
    setCookie('_autoplay_continued', 'false', 14)
    $('#autoplay-off').hide();
    $('#autoplay-on').css('display', 'inline-block');
});