import http from "k6/http";
import { sleep } from "k6";
import { check } from "k6";

import { FormData } from "https://jslib.k6.io/formdata/0.0.2/index.js";

import {getAnimation, generateAnimation} from "./sketch_api_calls.js";

const imageFile = open("./data/image.png", "b");

const HOST = "http://3.145.167.115:5000";

export function setup() {
  // // Init Code
  // // Step 1. Upload Image
  // const uuid = uploadImage(imageFile);
  // console.log("UUID", uuid);
  // setConsentAnswer(uuid);

  // // Step 3. Get Bounding box
  // const boundingBox = getBoundingBox(uuid);
  // const newboundingBox = setBoundingBox(uuid, boundingBox);

  // const mask = getMask(uuid);

  // const jointLocations = getJointLocations(test_uuid);
  // const setjointLocations = setJointLocations(test_uuid, jointLocations);

  // return uuid;

  // ***NOTE: use an existing uuid to load test or generate a new one from the above code.
  return "79d0be05ab6b43f58f22321ff5b3faf3";
}

export default function (uuid) {
  const test_uuid = clone_for_animation(uuid);
  console.log(test_uuid);

  // Step 4. get Animation
  generateAnimation(test_uuid, "running_jump");
  // getAnimation(test_uuid, "jab_cross");
  // getAnimation(test_uuid, "waving_gesture");
  //   sleep(10);
}

function clone_for_animation(src_uuid) {
  const res = http.post("http://localhost:9000/clone_animation_iterim_files", {
    src_uuid: src_uuid,
  });

  check(res, {
    "clone: is status 200": (r) => r.status === 200,
  });

  return res.body;
}
