
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

/**
 * Returns a cookie value given a name.
 * @param {String} cookieName 
 * @returns 
 */
export const getCookie = (cookieName: string) => {
  let name = cookieName + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) === 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

/**
 * Helper function to validate whether a given event is of type TouchEvent.
 * @param e 
 * @returns boolean
 */
export const isTouch = (e: React.TouchEvent | React.PointerEvent): e is React.TouchEvent => {
  return e.nativeEvent instanceof TouchEvent;
}