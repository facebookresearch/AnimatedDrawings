import axios from "axios";
import React, { useEffect, useState } from "react";
import { Button, Card, Spinner } from "react-bootstrap";
import { useHistory } from "react-router-dom";
import { useDrawingApi } from "../hooks/useDrawingApi";
import PoseEditor, { Pose, Position } from "./PoseEditor";

export interface Props {
  uuid: string | undefined;
}
export interface PoseModalProps extends Props {
  pose: Pose;
  setPose: (pose: Pose) => void;
}

const PoseStep = ({ uuid }: Props) => {
  // const { isLoading, uploadImage } = useDrawingApi((err) => {});
  let history = useHistory();
  const [pose, setPose] = useState<Pose>({ nodes: [], edges: [] });
  const { isLoading, setJointLocations } = useDrawingApi((err) => {
    console.log(err);
  });

  return (
    <Card className="border-0">
      <Card.Body>
        <Card.Title>Strike a pose</Card.Title>
        <Card.Text>Now let's adjust the pose!</Card.Text>
        <PoseModal uuid={uuid} pose={pose} setPose={setPose} />
      </Card.Body>
      <Card.Footer className="text-muted">
        <Button
          variant="secondary"
          onClick={() => {
            if (null === uuid && undefined === uuid) {
              return;
            }
            const joints = mapPoseToJoints(pose);

            console.log(joints);
            setJointLocations(uuid!, joints, () => {
              history.push(`/result/${uuid}`);
            });
          }}
        >
          Done
        </Button>
      </Card.Footer>
    </Card>
  );
};

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

const mapPoseToJoints = (pose: Pose) => {
  const entries = pose.nodes.reduce((agg, node) => {
    agg.push([node.label, node.position]);
    return agg;
  }, new Array<[string, any]>());
  console.log(entries);

  return Object.fromEntries(entries);
};

const PoseModal = ({ uuid, pose, setPose }: PoseModalProps) => {
  // const [isLoading, setIsLoading] = useState(true);

  const [imageUrl, setImageUrl] = useState<any>();
  const { isLoading, getJointLocations, getCroppedImage } = useDrawingApi(
    (err) => {
      console.log(err);
    }
  );

  useEffect(() => {
    // Load cropped Image
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
  }, [uuid]);

  const startPose = pose
    ? {
        nodes: Object.entries(pose).map((arr) => {
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
      }
    : null;

  return (
    <>
      {isLoading && <Spinner animation="border" />}
      {pose && <PoseEditor imageUrl={imageUrl} pose={pose} setPose={setPose} />}
    </>
  );
};

export default PoseStep;
