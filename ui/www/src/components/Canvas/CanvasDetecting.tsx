import React, { useEffect } from "react";
import { Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";

import { Position } from "../PoseEditor";
import Loader from "../Loader";

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

const CanvasDetecting = () => {
  const {
    drawing,
    uuid,
    imageUrlPose,
    setImageUrlPose,
    setPose,
  } = useDrawingStore();

  const {
    isLoading,
    getJointLocations,
    getCroppedImage,
  } = useDrawingApi((err) => {});
  const { setCurrentStep } = useStepperStore();

  /**
   * When an uuid is detected, invoke API to fetch a croppedImage with pose anotations.
   * The component will only rerender when the uuid dependency changes.
   * exhaustive-deps eslint warning was diable as no more dependencies are really necesary as side effects.
   * Contrary to this, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchCroppedImage = async () => {
      try {
        await getCroppedImage(uuid!, (data) => {
          let reader = new window.FileReader();
          reader.readAsDataURL(data);
          reader.onload = function () {
            let imageDataUrl = reader.result;
            setImageUrlPose(imageDataUrl);
          };
        });

        getJointLocations(uuid!, (data) => {
          const mappedPose = mapJointsToPose(data);
          setPose(mappedPose);
        });
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchCroppedImage();

    return () => {};
  }, [uuid]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {isLoading ? (
          <Loader drawingURL={drawing} />
        ) : (
          <img src={imageUrlPose} alt="Drawing Detected"></img>
        )}
      </div>

      {isLoading ? (
        <div className="mt-3">
          <button className="buttons large-button">
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
          </button>
        </div>
      ) : (
        <div className="mt-3 text-center">
          <button
            className="buttons large-button ml-1"
            onClick={() => setCurrentStep(4)}
          >
            Next <i className="bi bi-arrow-right px-2" />
          </button>
        </div>
      )}
    </div>
  );
};

export default CanvasDetecting;
