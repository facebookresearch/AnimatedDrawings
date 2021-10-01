
/**
 * A function to resize a binary image given width and height as params
 * @param datas 
 * @param wantedWidth 
 * @param wantedHeight 
 * @returns a new uri representing a resized image.
 */
export const resizedataURL = (
  datas: string,
  wantedWidth: number,
  wantedHeight: number
) => {
  return new Promise(async function (resolve, reject) {
    // We create an image to receive the Data URI
    var img = document.createElement("img") as HTMLImageElement;
    // When the event "onload" is triggered we can resize the image.
    img.onload = function () {
      var canvas = document.createElement("canvas");
      var ctx = canvas.getContext("2d");
      canvas.width = wantedWidth;
      canvas.height = wantedHeight;
      ctx?.drawImage(img, 0, 0, wantedWidth, wantedHeight);
      var dataURI = canvas.toDataURL();
      resolve(dataURI);
    };
    img.src = datas;
  });
};

/**
 * Returns a calcualted ratio to make cropped image fit inside the canvas component, 
 * requeired for mobile screens.
 * @param {Number} canvasWidth 
 * @param {Number} canvasHeight 
 * @param {Number} oW Original cropped image width
 * @param {Number} oH Original cropped image height
 * @returns 
 */
export const calculateRatio = (
  canvasWidth: number,
  canvasHeight: number,
  oW: number,
  oH: number 
) => {
  if (Math.min(canvasHeight, canvasHeight) > Math.max(oW, oH)) {
    return 1;
  } else if (oH >= oW && canvasHeight >= canvasWidth) {
    return canvasHeight / oH;
  } else if (oH < oW && canvasHeight >= canvasWidth) {
    return canvasHeight / oW;
  } else if (oH >= oW && canvasHeight < canvasWidth) {
    return canvasWidth / oH;
  } else {
    return canvasWidth / oW;
  }
};