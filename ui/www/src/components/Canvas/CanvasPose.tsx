// * Not used at the moment.
import React, { useState, useEffect } from "react";
//import { useHistory } from "react-router-dom";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";

import PoseEditor, { Position } from "../PoseEditor";

const mapJointsToPose = (joints: object) => {
  return {
    nodes: Object.entries(joints).map((arr) => {
      return { id: arr[0], label: arr[0], position: arr[1] as Position };
    }),
    edges: [
      // Right side
      {
        from: "right_shoulder",
        to: "right_elbow",
      },
      {
        from: "right_elbow",
        to: "right_wrist",
      },
      {
        from: "right_shoulder",
        to: "right_hip",
      },
      {
        from: "right_hip",
        to: "right_knee",
      },
      {
        from: "right_knee",
        to: "right_ankle",
      },
      // Left side
      {
        from: "left_shoulder",
        to: "left_elbow",
      },
      {
        from: "left_elbow",
        to: "left_wrist",
      },
      {
        from: "left_shoulder",
        to: "left_hip",
      },
      {
        from: "left_hip",
        to: "left_knee",
      },
      {
        from: "left_knee",
        to: "left_ankle",
      },
      // Shoulders and hips
      {
        from: "left_shoulder",
        to: "right_shoulder",
      },
      {
        from: "left_hip",
        to: "right_hip",
      },
      // face
      {
        from: "nose",
        to: "left_eye",
      },
      {
        from: "nose",
        to: "right_eye",
      },
      {
        from: "nose",
        to: "left_ear",
      },
      {
        from: "nose",
        to: "right_ear",
      },
      {
        from: "nose",
        to: "left_shoulder",
      },
      {
        from: "nose",
        to: "right_shoulder",
      },
    ],
  };
};

const CanvasPose = () => {
  //const history = useHistory();
  const { uuid, pose, setPose } = useDrawingStore();

  const [imageUrl, setImageUrl] = useState<any>();
  const { getJointLocations, getCroppedImage } = useDrawingApi((err) => {
    console.log(err);
  });

  useEffect(() => {
    getCroppedImage(uuid!, (data) => {
      let reader = new window.FileReader();
      reader.readAsDataURL(data);
      reader.onload = function () {
        let imageDataUrl = reader.result;
        setImageUrl(imageDataUrl);
      };
    });

    getJointLocations(uuid!, (data) => {
      const mappedPose = mapJointsToPose(data);
      setPose(mappedPose);
    });

    return () => {};
  }, [uuid]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {pose && (
          <PoseEditor imageUrl={imageUrl} pose={pose} setPose={setPose} />
        )}
      </div>

      <div className="mt-3">
        <button className="large-button border border-dark">
          <i className="bi bi-camera-fill mr-1" />
        </button>
      </div>
    </div>
  );
};

export default CanvasPose;
