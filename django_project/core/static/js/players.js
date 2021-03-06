/* append the YouTube IFRAME API script */


var youtube = document.createElement('script');
youtube.type = "text/javascript";
youtube.src = "//www.youtube.com/iframe_api";

var s = document.getElementsByTagName('script')[0];
s.parentNode.insertBefore(youtube, s);

$(window).load(function () {
    var i = 0;

    var startButtons = document.getElementsByClassName('pq-slim-quote-picture', i);
    var mobileStartButtons = document.getElementsByClassName('mobile-start-button', i);
    var hiddenButton;
    var audioSourceMP3 = [];
    var YouTubeIDs = [];
    var timeBegins = [];
    var timeEnds = [];

    var playerWrappers = document.getElementsByClassName('player');
    
    var openPlayerWrapper = false;
    
    for (i = 0; i < startButtons.length; ++i) {
        startButtons[i].addEventListener("click", playMedia(i));
        mobileStartButtons[i].addEventListener("click", playMedia(i));
        audioSourceMP3[i] = startButtons[i].getAttribute('audioSourceMP3');
        YouTubeIDs[i] = startButtons[i].getAttribute('YouTubeID');
        timeBegins[i] = startButtons[i].getAttribute('timeBegins');
        timeEnds[i] = startButtons[i].getAttribute('timeEnds');
    }
    
    window.playerWrappers = playerWrappers;
    window.openPlayerWrapper = openPlayerWrapper;
    window.startButtons = startButtons;
    window.mobileStartButtons = mobileStartButtons;
    window.hiddenButton = hiddenButton;
    window.audioSourceMP3 = audioSourceMP3;
    window.YouTubeIDs = YouTubeIDs;
    window.timeBegins = timeBegins;
    window.timeEnds = timeEnds;
    
    function playMedia(i) {
        return function () {
            if (openPlayerWrapper != false) {
                try {
                    var openPlayer = document.getElementById('open-player');
                    openPlayer.parentNode.className = "player";
                    $('#open-player').remove();
                }
                catch(err) {
                    // pass
                } 
                $(hiddenButton).show();
                hiddenButton = startButtons[i];
                $(startButtons[i]).hide();
            } else {
                openPlayerWrapper = true;
                hiddenButton = startButtons[i];
                $(startButtons[i]).hide();
            }
            if (i != 0) {
                window.location.hash = '#pq-quote-' + (i + 1);
            }
            if (YouTubeIDs[i].length == 11) {
                function onYouTubeIframeAPIReady() {
                    var YouTubeNode = document.createElement('div');
                    YouTubeNode.setAttribute('id', 'open-player');
                    playerWrappers[i].appendChild(YouTubeNode);
                    YouTubeNode.parentNode.className = YouTubeNode.parentNode.className + " youtube-player";
                    
                    var playerNode = document.getElementById('open-player').parentNode;
                    $(playerNode).css('margin', '5px 0 15px 0');
                  
                    playerWrappers[i] = new YT.Player(YouTubeNode, {
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
                // loadVideoById does not work on most mobile devices
                  
                 if (typeof window.orientation == 'undefined') {
                    function onPlayerReady(event) {
                        event.target.loadVideoById({ 
                            videoId: YouTubeIDs[i],
                            startSeconds: timeBegins[i],
                            endSeconds: timeEnds[i]
                        });
                      };
                 } else {
                    function onPlayerReady(event) {
                        event.target.cueVideoById({ 
                            videoId: YouTubeIDs[i],
                            startSeconds: timeBegins[i],
                            endSeconds: timeEnds[i]
                        });
                      };
                 }
                  var done = false;
                  function onPlayerStateChange(event) {
                      if (event.data == 0) {
                          done = true;
                          event.target.destroy();
                          $(hiddenButton).show();
                          var YouTubeNode = document.getElementById('open-player');
                          YouTubeNode.parentNode.className = "player";
                          $('#open-player').remove();
                      }
                  };
                  onYouTubeIframeAPIReady();
                    
            } else {
                var audio = document.createElement('audio');
                audio.setAttribute('controls', '');
                audio.setAttribute('preload', 'metadata');
                audio.setAttribute('id', 'open-player');
                playerWrappers[i].appendChild(audio);
                
                var source = document.createElement('source');
                source.setAttribute('src', audioSourceMP3[i]);
                audio.appendChild(source);
                
                var playerNode = document.getElementById('open-player').parentNode;
                $(playerNode).css('margin', '5px 0 10px 0');

                audio.load();
                audio.onloadedmetadata = function() { 
                    audio.play();
                };
                
                audio.addEventListener('timeupdate', function() {
                    if (Math.floor(audio.currentTime) == timeEnds[i]) {
                        audio.pause();
                        audio.currentTime = parseInt(Math.floor(timeEnds[i])) + 1;
                    }
                    if (timeBegins[i] != null && timeBegins[i] > 5 ) {
                        if (audio.currentTime == 0) {
                            audio.currentTime = timeBegins[i];
                        } else if (audio.currentTime < 5) {
                            audio.currentTime = timeBegins[i];
                        }
                    }
                    
                },false);
            }
        }
    }
    
});


/* Sample MP3: http://traffic.libsyn.com/joeroganexp/p523.mp3 */
/* Sample OGG: http://www.tuxradar.com/files/podcast/tuxradar_s06e02.ogg */

// HACK solution to check if person is using a mobile browser
if (typeof window.orientation == 'undefined') {
  //
}


// Alert Chrome users that clicked a highlight 1-time
//  that Chrome is not optimal for viewing highlights
var alertedChrome = getCookie('_alertedChrome');
var is_chrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;



if (is_chrome == true  && alertedChrome != 'true') {
    if (typeof window.orientation == 'undefined') {
          alert('Attn Chrome user: Podverse is in beta. Full episodes will work well on Chrome, but episode highlights currently load faster on Firefox, IE, or Safari.');
          setCookie('_alertedChrome', 'true', 14)
    }
};