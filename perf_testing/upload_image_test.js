import http from "k6/http";
import { sleep } from "k6";
import { check } from "k6";

import { FormData } from "https://jslib.k6.io/formdata/0.0.2/index.js";

const imageFile = open("./data/image.png", "b");
// const maskFile = open("./data/mask.png", "b");

const HOST = "http://localhost:5000";

const ROUTES = {
  upload_image: "upload_image",
  set_consent_answer: "set_consent_answer",
  get_bounding_box_coordinates: "get_bounding_box_coordinates",
  set_bounding_box_coordinates: "set_bounding_box_coordinates",
  get_mask: "get_mask",
  set_mask: "set_mask",
  get_cropped_image: "get_cropped_image",
  get_joint_locations_json: "get_joint_locations_json",
  set_joint_locations_json: "set_joint_locations_json",
  get_animation: "get_animation",
};

function getRouteUrl(route) {
  return HOST + "/" + route;
}

export default function () {
  // Step 1. Upload Image
  const uuid = uploadImage();
  console.log("UUID", uuid);
  // Step 2. Set Consent
  //   sleep(3);
  setConsentAnswer(uuid);

  //   // Step 3. Get Bounding box
  const boundingBox = getBoundingBox(uuid);
  console.log("bouding Box", JSON.stringify(boundingBox));
  const newboundingBox = setBoundingBox(uuid, boundingBox);

  console.log("new bouding Box", JSON.stringify(newboundingBox));

  const mask = getMask(uuid);
  console.log("mask", typeof mask);
  //   const newMask = setMask(uuid, mask);
  //   const croppedImage = getCroppedImage(uuid);
  const jointLocations = getJointLocations(uuid);
  const setjointLocations = setJointLocations(uuid, jointLocations);

  // Step 4. get Animation
  getAnimation(uuid, "running_jump");
  //   sleep(10);
}

function uploadImage() {
  const data = {
    file: http.file(imageFile, "file"),
  };

  const res = http.post(getRouteUrl(ROUTES.upload_image), data);
  check(res, {
    "uploadImage: is status 200": (r) => r.status === 200,
  });

  const uuid = res.body;
  return uuid;
}

function setConsentAnswer(uuid) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });
  formData.append("consent_response", {
    data: "0",
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.set_consent_answer),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  check(res, {
    "setConsentAnswer: is status 200": (r) => r.status === 200,
  });
}

function getBoundingBox(uuid) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.get_bounding_box_coordinates),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  check(res, {
    "getBoundingBox: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

function setBoundingBox(uuid, boundingBox) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });
  formData.append("bounding_box_coordinates", {
    data: boundingBox,
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.set_bounding_box_coordinates),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  check(res, {
    "setBoundingBox: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

// Get Mask
function getMask(uuid) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });

  const res = http.post(getRouteUrl(ROUTES.get_mask), formData.body(), {
    headers: {
      "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
    },
  });
  check(res, {
    "getMask: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

// Set Mask
function setMask(uuid, maskFile) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });
  formData.append("file", http.file(maskFile, "file.png", "image/png"));

  const res = http.post(getRouteUrl(ROUTES.set_mask), formData.body(), {
    headers: {
      "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
    },
  });
  check(res, {
    "setMask: is status 200": (r) => r.status === 200,
  });

  return res.data;
}

// Get Cropped Image
function getCroppedImage(uuid) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.get_cropped_image),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  check(res, {
    "getCroppedImage: is status 200": (r) => r.status === 200,
  });

  return res.data;
}

// Get Joint Locations
function getJointLocations(uuid) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.get_joint_locations_json),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  check(res, {
    "getJointLocations: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

// Set Joint Locations
function setJointLocations(uuid, joints) {
  let formData = new FormData();
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });
  formData.append("joint_location_json", {
    data: joints,
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.set_joint_locations_json),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  check(res, {
    "setJointLocations: is status 200": (r) => r.status === 200,
  });

  return res.data;
}

function getAnimation(uuid, animation) {
  let formData = new FormData();
  formData.append("animation", {
    data: animation, //"running_jump",
    content_type: "text/plain",
  });
  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });

  const res = http.post(getRouteUrl(ROUTES.get_animation), formData.body(), {
    headers: {
      "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
    },
  });
  check(res, {
    "getAnimation: is status 200": (r) => r.status === 200,
  });

  return res.data;
}
