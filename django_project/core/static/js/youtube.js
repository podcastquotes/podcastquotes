var videoPlayers = []
for (var i=1; i < 11; i++) {
    videoPlayers.push(document.getElementById("youtube-player-wrapper-" + i));
}

console.log(videoPlayers);

var startButtons = []
for (var i=1; i < 11; i++) {
    startButtons.push(document.getElementById("youtube-start-button-wrapper-" + i));
}

console.log(startButtons);

var xsStartButtons = []
for (var i=1; i < 11; i++) {
    xsStartButtons.push(document.getElementById("xs-youtube-start-button-wrapper-" + i));
}

console.log(xsStartButtons);

for (var i=0; i < 10; i++) {
  
  var forloopCounter = i + 1;
  
  console.log("hello");
  
  if(startButtons[i].childNodes[1] == null) {continue;}
  
  var getFullId = startButtons[i].childNodes[1];
  
  var youtubeOnlyId = getFullId.id.substring(0,11);
  
  startButtons[i].onclick = function () {
    
    var getStartElement = this.childNodes[1];

    var getPlayerId = getStartElement.childNodes[1].id - 1;

    // Create an iFrame with autoplay set to true
    var iframe = document.createElement("iframe");
    iframe.setAttribute("src",
          "https://www.youtube.com/embed/" + getStartElement.id
        + "autoplay=1&autohide=1&border=0&wmode=opaque&enablejsapi=1");
    
    // The height and width of the iFrame should be the same as parent
    iframe.setAttribute("class", "iframe-size");
      
    // Replace the YouTube thumbnail with YouTube HTML5 Player
    this.style.display = 'none';
    
    videoPlayers[getPlayerId].appendChild(iframe);
 
  };
  
}

for (var i=0; i < 10; i++) {
  
  var forloopCounter = i + 1;
  
  if(xsStartButtons[i].childNodes[1] == null) {continue;}
  
  var getFullId = xsStartButtons[i].childNodes[1];
  
  var youtubeOnlyId = getFullId.id.substring(0,11);
  
  xsStartButtons[i].onclick = function () {
    
    var getStartElement = this.childNodes[1];
    
    var getPlayerId = getStartElement.childNodes[1].id - 1;

    // Create an iFrame with autoplay set to true
    var iframe = document.createElement("iframe");
    iframe.setAttribute("src",
          "https://www.youtube.com/embed/" + getStartElement.id
        + "autoplay=1&autohide=1&border=0&wmode=opaque&enablejsapi=1");
    
    // The height and width of the iFrame should be the same as parent
    iframe.setAttribute("class", "iframe-size");
      
    // Replace the YouTube thumbnail with YouTube HTML5 Player
    this.style.display = 'none';
    
    videoPlayers[getPlayerId].appendChild(iframe);
 
  };
  
}