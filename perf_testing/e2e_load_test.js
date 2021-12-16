import http from "k6/http";
import { sleep } from "k6";
import { check } from "k6";

import { FormData } from "https://jslib.k6.io/formdata/0.0.2/index.js";

import {
  uploadImage,
  setConsentAnswer,
  getBoundingBox,
  setBoundingBox,
  getMask,
  getJointLocations,
  setJointLocations,
  getAnimation,
  testTimimgs,
} from "./sketch_api_calls.js";

const imageFile = open("./data/image.png", "b");
const USER_SLEEP = 10;

const HOST = "https://beta-sketch-api.metademolab.com";

export const options = {
  stages: [
    { duration: "1m", target: 50 },
    { duration: "1m", target: 100 },
    { duration: "1m", target: 150 },
    { duration: "1m", target: 200 },
    { duration: "1m", target: 250 },
    { duration: "1m", target: 350 },
    { duration: "1m", target: 450 },
  ],
};

export default function () {
  // Step 1. Upload Image
  const uuid = uploadImage(imageFile);
  console.log("UUID", uuid);

  // Step 2. Set Consent
  sleep(USER_SLEEP);
  setConsentAnswer(uuid);

  // Step 3. Get Bounding box
  const boundingBox = getBoundingBox(uuid);
  const newboundingBox = setBoundingBox(uuid, boundingBox);
  sleep(USER_SLEEP);

  // Step 4. Get Mask
  const mask = getMask(uuid);
  sleep(USER_SLEEP);

  // Step 5. get Pose
  const jointLocations = getJointLocations(uuid);
  const setjointLocations = setJointLocations(uuid, jointLocations);
  sleep(USER_SLEEP);

  // Step 6. get Get Animation
  getAnimation(uuid, "running_jump");
  sleep(USER_SLEEP);
}
