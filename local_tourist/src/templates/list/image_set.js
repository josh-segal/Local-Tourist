require('dotenv').config();

var imgs = document.getElementsByClassName("place_img");

for (var i = 0; i < imgs.length; i++) {
  console.log(imgs[i]);
  imgs[i].src = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=" + imgs[i].src.substring(imgs[i].src.lastIndexOf("/") + 1) + "&key=" + process.env.API_KEY;
}