// Find all the YouTube video embedded on a page
var videos = document.getElementsByClassName("youtube");
 
for (var i=0; i<videos.length; i++) {
  
  var youtube = videos[i];
  
  var youtubeOnlyId = youtube.id.substring(0,11);
  
  // Based on the YouTube ID, we can easily find the thumbnail image
  
  var preview = document.createElement("div");
  preview.setAttribute("class", "preview");
  
  var img = document.createElement("img");
  img.setAttribute("src", "http://i.ytimg.com/vi/"
                          + youtubeOnlyId + "/hqdefault.jpg");
  img.setAttribute("class", "youtube-img-preview");
  
 
  // Overlay the Play icon to make it look like a video player
  var circle = document.createElement("i");
  circle.setAttribute("class","circle fa fa-play-circle-o");  
  
  youtube.appendChild(preview);
  youtube.appendChild(img);
  preview.appendChild(circle);
  
  // Attach an onclick event to the YouTube Thumbnail
  youtube.onclick = function() {
 
    // Create an iFrame with autoplay set to true
    var iframe = document.createElement("iframe");
    iframe.setAttribute("src",
          "https://www.youtube.com/embed/" + this.id
        + "autoplay=1&autohide=1&border=0&wmode=opaque&enablejsapi=1");
    
    // The height and width of the iFrame should be the same as parent
    iframe.setAttribute("class", "iframe-size");
      
    // Replace the YouTube thumbnail with YouTube HTML5 Player
    this.parentNode.replaceChild(iframe, this);
 
  };
}