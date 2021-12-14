import http from "k6/http";
import { sleep } from "k6";
import { check } from "k6";

import { FormData } from "https://jslib.k6.io/formdata/0.0.2/index.js";

export const options = {
  scenarios: {
    // vu_1: {
    //   executor: "constant-vus",
    //   vus: 1,
    //   duration: "1m",
    // },
    // vu_10: {
    //   executor: "constant-vus",
    //   vus: 10,
    //   duration: "1m",
    // },
    vu_20: {
      executor: "constant-vus",
      vus: 20,
      duration: "1m",
    },
    // vu_100: {
    //   executor: "constant-vus",
    //   vus: 100,
    //   duration: "1m",
    // },
  },
};

const imageFile = open("./data/cropped_d2_image.png", "b");
// const maskFile = open("./data/mask.png", "b");

// const HOST = "http://localhost:5911/predictions/D2_humanoid_detector";
// FARGATE
const HOST =
  "http://ml-devops-alb-QA-977298474.us-east-2.elb.amazonaws.com:5911/predictions/D2_humanoid_detector";

function getRouteUrl(route) {
  return HOST + "/" + route;
}

export default function () {
  // Step 1. Upload Image
  uploadImage();
}

function uploadImage() {
  const data = {
    file: http.file(imageFile, "file"),
  };

  const res = http.post(HOST, imageFile);
  check(res, {
    "uploadImage: is status 200": (r) => r.status === 200,
  });

  const body = res.body;
  console.log(body);
  return body;
}
