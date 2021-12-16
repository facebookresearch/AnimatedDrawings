import http from "k6/http";
import { sleep } from "k6";
import { Trend } from "k6/metrics";
import { check } from "k6";

import { FormData } from "https://jslib.k6.io/formdata/0.0.2/index.js";

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
  generate_animation: "generate_animation",
};

const uploadImageTrend = new Trend("upload_image");
const consentTrend = new Trend("set_consent_answer")
const get_bounding_box_coordinates_trend = new Trend("get_bounding_box_coordinates"); 
const set_bounding_box_coordinates_trend = new Trend("set_bounding_box_coordinates");
const get_mask_trend = new Trend("get_mask");
const set_mask_trend = new Trend("set_mask");
const get_cropped_image_trend = new Trend("get_cropped_image");
const get_joint_locations_json_trend = new Trend("get_joint_locations_json");
const set_joint_locations_json_trend = new Trend("set_joint_locations_json");
const get_animation_trend = new Trend("get_animation");
const generate_animation_trend = new Trend("generate_animation");

export function getRouteUrl(route) {
  return HOST + "/" + route;
}

export function testTimimgs(imageFile) {
  uploadImageTrend.add(1000);
  uploadImageTrend.add(2000);
  uploadImageTrend.add(3000);
}

export function uploadImage(imageFile) {
  const data = {
    file: http.file(imageFile, "file"),
  };

  const res = http.post(getRouteUrl(ROUTES.upload_image), data);
  uploadImageTrend.add(res.timings.waiting);
  check(res, {
    "uploadImage: is status 200": (r) => r.status === 200,
  });

  const uuid = res.body;
  return uuid;
}

export function setConsentAnswer(uuid) {
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
  consentTrend.add(res.timings.waiting);
  check(res, {
    "setConsentAnswer: is status 200": (r) => r.status === 200,
  });
}

export function getBoundingBox(uuid) {
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
  get_bounding_box_coordinates_trend.add(res.timings.waiting);
  check(res, {
    "getBoundingBox: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

export function setBoundingBox(uuid, boundingBox) {
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
  set_bounding_box_coordinates_trend.add(res.timings.waiting);
  check(res, {
    "setBoundingBox: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

// Get Mask
export function getMask(uuid) {
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
  get_mask_trend.add(res.timings.waiting)
  check(res, {
    "getMask: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

// Set Mask
export function setMask(uuid, maskFile) {
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
  set_mask_trend.add(res.timings.waiting)
  check(res, {
    "setMask: is status 200": (r) => r.status === 200,
  });

  return res.data;
}

// Get Cropped Image
export function getCroppedImage(uuid) {
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
  get_cropped_image_trend.add(res.timings.waiting)
  check(res, {
    "getCroppedImage: is status 200": (r) => r.status === 200,
  });

  return res.data;
}

// Get Joint Locations
export function getJointLocations(uuid) {
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
  get_joint_locations_json_trend.add(res.timings.waiting)
  check(res, {
    "getJointLocations: is status 200": (r) => r.status === 200,
  });

  return res.body;
}

// Set Joint Locations
export function setJointLocations(uuid, joints) {
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
  set_joint_locations_json_trend.add(res.timings.waiting)
  check(res, {
    "setJointLocations: is status 200": (r) => r.status === 200,
  });

  return res.data;
}

export function getAnimation(uuid, animation) {
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
  get_animation_trend.add(res.timings.waiting)
  check(res, {
    "getAnimation: is status 200": (r) => r.status === 200,
  });

  return res.data;
}
export function generateAnimation(uuid, animation) {
  let formData = new FormData();

  formData.append("uuid", {
    data: uuid,
    content_type: "text/plain",
  });
  formData.append("animation_type", {
    data: animation, //"running_jump",
    content_type: "text/plain",
  });

  const res = http.post(
    getRouteUrl(ROUTES.generate_animation),
    formData.body(),
    {
      headers: {
        "Content-Type": "multipart/form-data; boundary=" + formData.boundary,
      },
    }
  );
  generate_animation_trend.add(res.timings.waiting)
  check(res, {
    "generateAnimation: is status 200": (r) => r.status === 200,
  });

  return res.data;
}
