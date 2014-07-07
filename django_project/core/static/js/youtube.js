/*
 
  YouTube Embed Code
  
  Author:   Amit Agarwal
  Blog:     www.labnol.org
  Date:     04/15/2013
  Modified by: Podverse, July 2014
 
*/

/* ***********************************************************************
   -SECTION 1 is for setting and checking the autoplay cookie.
   -SECTION 2 append the YouTube IFRAME API Script.
   -SECTION 3 is for the single YouTube player by itself on the quote page.
   -SECTION 4 is for the multiple YouTube players (from forloop) on all other pages.
************************************************************************** */

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


/* SECTION 2 */
/* append the YouTube IFRAME API script */


var youtube = document.createElement('script');
youtube.type = "text/javascript";
youtube.src = "//www.youtube.com/iframe_api";

var s = document.getElementsByTagName('script')[0];
s.parentNode.insertBefore(youtube, s);

/* SECTION 3 */
/* single YouTube player loaded by itself on the quote page */

$(window).load(function () {
    var nodeAlone = "youtube-player-alone";
    window.nodeAlone = nodeAlone;

    if (document.getElementById(nodeAlone)) {
        var playerAlone;

        // Read all the parameter of the DIV tag and store as global variables
        var paramsAlone = document.getElementById(nodeAlone);
        window.paramsAlone = paramsAlone;

        var startTimeAlone = paramsAlone.getAttribute("startTime");
        window.startTimeAlone = startTimeAlone;
        
        var endTimeAlone = paramsAlone.getAttribute("endTime");
        window.endTimeAlone = endTimeAlone;
        
        var videoIDAlone = paramsAlone.getAttribute("videoID");
        window.videoIDAlone = videoIDAlone;
        
        var nextVideoURLAlone = paramsAlone.getAttribute('nextVideoURL');
        window.nextVideoURLAlone = nextVideoURLAlone;
        
        startVideoAlone();
        
    };
});

function startVideoAlone() {
    onYouTubeIframeAPIReady();
    
    // Prepare the YouTube Player
    function onYouTubeIframeAPIReady() {
      playerAlone = new YT.Player(nodeAlone, {
        playerVars: {'rel': 0, 'showinfo': 0, 'hidecontrols': 1 },
        events: {
          'onReady': onPlayerReady,
          'onStateChange': onPlayerStateChange,
        }
      });
    }
    
    // When the player is ready, we load the video.
    // loadVideoById starts the video automatically.
    // cueVideoById does not start the video automatically.
    function onPlayerReady(event) {      
      var autoplayOn = getCookie('_autoplay');
      if (autoplayOn==='true') {
          event.target.loadVideoById({ 
            videoId: videoIDAlone,
            startSeconds: startTimeAlone,
            endSeconds: endTimeAlone
          });  
      } else {
          event.target.cueVideoById({ 
            videoId: videoIDAlone,
            startSeconds: startTimeAlone,
            endSeconds: endTimeAlone
          });
      }
    }

    var done = false;
    function onPlayerStateChange(event) {
        if (event.data == 0) {
            done = true;
            if (nextVideoURLAlone != '') {
                playNextVideoAlone();
            } else {
            // do nothing
            }
        }
    };

    function playNextVideoAlone() {
        var autoplayOn = getCookie('_autoplay');
        if (autoplayOn == 'true') {
            window.location.href = nextVideoURLAlone;
        } else {
            // do nothing
        }
    };

};

/* SECTION 4 */
/* multiple YouTube players loaded on home, podcast, episode, and user pages */

$(window).load(function () {
    var videoPlayerWrappers = document.getElementsByClassName('youtube-player-wrapper', i);
    var startButtonWrappers = document.getElementsByClassName('youtube-start-button-wrapper', i);
    var quoteWrappers = document.getElementsByClassName('pq-quote', i);
    var players = [];
    var nodes = [];
    var params = [];
    var startTimes = [];
    var endTimes = [];
    var videoIDs = [];
    var nextPageButton = document.getElementById('next-page');

    for (var i=0; i < 10; i++) {
        players[i] = 'player' + i;
        nodes[i] = 'youtube-player-' + (i + 1);
        params[i] = document.getElementById(nodes[i]);
        if (params[i] != null) {
            startTimes[i] = params[i].getAttribute('startTime');
            endTimes[i] = params[i].getAttribute('endTime');
            videoIDs[i] = params[i].getAttribute('videoID');
        }
    }

    // Set as global variables so continueVideos() will work
    window.videoPlayerWrappers = videoPlayerWrappers;
    window.startButtonWrappers = startButtonWrappers;
    window.players = players;
    window.nodes = nodes;
    window.params = params;
    window.startTimes = startTimes;
    window.endTimes = endTimes;
    window.videoIDs = videoIDs;
    window.nextPageButton = nextPageButton;

    for (var i=0; i < 10; i++) {
        if (startButtonWrappers[i] != null) {
            startButtonWrappers[i].addEventListener("click", startVideo(i));
        }
    }
});

function startVideo(i) {
    "use strict";
    return function () {
        $(startButtonWrappers[i]).hide();
        $(videoPlayerWrappers[i]).show();
        onYouTubeIframeAPIReady();
    
        function onYouTubeIframeAPIReady() {
          players[i] = new YT.Player(nodes[i], {
            playerVars: {'rel': 0, 'showinfo': 0, 'hidecontrols': 1 },
            events: {
              'onReady': onPlayerReady,
              'onStateChange': onPlayerStateChange,
            }
          });
        }

        // When the player is ready, we load the video.
        // loadVideoById starts the video automatically.
        // cueVideoById does not start the video automatically.
        function onPlayerReady(event) {
          event.target.loadVideoById({ 
            videoId: videoIDs[i],
            startSeconds: startTimes[i],
            endSeconds: endTimes[i]
          });  
        }

        var done = false;
        function onPlayerStateChange(event) {
            if (event.data == 0) {
                done = true;
                playNextVideo();
            }
        };
        
        function playNextVideo() {
            var autoplayOn = getCookie('_autoplay');
            if (autoplayOn == 'true') {
                for (var j=1; j < 9; j++) {
                    if (videoIDs[i + j] != 'None' && videoIDs[i + j] != undefined) {
                        startButtonWrappers[i + j].click();
                        window.location.hash = '#pq-quote-' + (i + j + 1);
                        break;
                    } else if (i + j + 1 > 10 && nextPageButton != null) {
                        setCookie('_autoplay_continued', 'true', 14)
                        nextPageButton.click();
                        break;
                    }
                }
            } else {
                // do nothing
            }
        };
        
    };
};

 
$(window).load(function () {
    // autoplayOnContinued prevents videos from starting automatically
    // when you first visit a page. The cookie is set to true after the
    // last video on the page has been played, and is set back to false
    // after the first video on the next page begins.

    var autoplayOnContinued = getCookie('_autoplay_continued');

    if (autoplayOnContinued=='true') {
        continueVideos();
        var autoplayOnContinued = setCookie('_autoplay_continued', 'false', 14);
    }
    
    function continueVideos() {
        for (var i=0; i < 10; i++) {
            if (videoIDs[i] != 'None' && videoIDs[i] != undefined) {
                startButtonWrappers[i].click();
                window.location.hash = '#pq-quote-' + (i + 1);
                break
            }
        }
    }
});