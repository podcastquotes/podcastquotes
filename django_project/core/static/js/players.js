$(window).load(function () {
    var i = 0;

    var startButtons = document.getElementsByClassName('pq-slim-quote-picture', i);
    var audioSourceMP3 = [];
    var timeBegins = [];
    var timeEnds = [];

    var playerWrappers = document.getElementsByClassName('player');
    
    var openPlayerWrapper = false;
    
    for (i = 0; i < startButtons.length; ++i) {
        startButtons[i].addEventListener("click", playMedia(i));
        audioSourceMP3[i] = startButtons[i].getAttribute('audioSourceMP3');
        timeBegins[i] = startButtons[i].getAttribute('timeBegins');
        timeEnds[i] = startButtons[i].getAttribute('timeEnds');
    }
    
    window.playerWrappers = playerWrappers;
    window.openPlayerWrapper = openPlayerWrapper;
    window.startButtons = startButtons;
    window.audioSourceMP3 = audioSourceMP3;
    window.timeBegins = timeBegins;
    window.timeEnds = timeEnds;
    
});

function playMedia(i) {
    return function () {
        if (openPlayerWrapper != false) {
            $('#open-audio').remove();
        } else {
            openPlayerWrapper = true;
        }
        var audio = document.createElement('audio');
        audio.setAttribute('controls', '');
        audio.setAttribute('preload', 'metadata');
        audio.setAttribute('id', 'open-audio');
        playerWrappers[i].appendChild(audio);

        var source = document.createElement('source');
        source.setAttribute('src', audioSourceMP3[i]);
        audio.appendChild(source);
        
        $(playerWrappers[i]).css('margin', '10px 0 5px 0');

        audio.load();
        audio.onloadedmetadata = function() { 
            audio.currentTime = timeBegins[i];
        };
        audio.onloadeddata = function() { 
            audio.play();
        };
                    
        audio.addEventListener('timeupdate', function() {
            if (timeEnds[i] && audio.currentTime >= timeEnds[i]) {
                audio.pause();
                audio.currentTime = timeBegins[i];
            }
        },false);
        
    }
}

/*
$(audio).bind('timeupdate', function () {
    if (audio.currentTime >= timeEnds[i]) { 
        audio.pause();
    }
});
*/

/*
audio.addEventListener('timeupdate', function() {
    if (timeEnds[i] && audio.currentTime >= timeEnds[i]) {
        audio.pause();
        audio.currentTime = timeBegins[i];
    }
},false);
*/

/*
var ctx = new webkitAudioContext();
 
function loadMusic(url) {
  var req = new XMLHttpRequest();
  req.open('GET', 'http://www.jplayer.org/audio/m4a/Miaow-07-Bubble.m4a', true);
  // req.setRequestHeader('Access-Control-Allow-Origin', '*');
  req.responseType = 'arraybuffer';
  // req.setRequestHeader("Range", "bytes=100-200");
  console.log('here');
  req.onload = function() {
    ctx.decodeAudioData(req.response, playSound);
  };
 console.log('there');
  req.send();
}
 
function playSound(buffer) {
  var src = ctx.createBufferSource();
  src.buffer = buffer;
  console.log("everywhere");
  src.connect(ctx.destination);
  // Play now!
  src.start(0);
}
*/

/* http://traffic.libsyn.com/joeroganexp/p523.mp3 */
/*http://www.tuxradar.com/files/podcast/tuxradar_s06e02.ogg */