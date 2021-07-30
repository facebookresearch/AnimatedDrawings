import axios from "axios";
import React, { useEffect, useState } from "react";
import { Button, Card, Spinner } from "react-bootstrap";
import PoseEditor, { Pose, Position } from "./PoseEditor";

export interface Props {
  uuid: string | undefined;
}

export const PoseStep = ({ uuid }: Props) => {
  // const { isLoading, uploadImage } = useDrawingApi((err) => {});

  return (
    <Card className="border-0">
      <Card.Body>
        <Card.Title>Strike a pose</Card.Title>
        <Card.Text>Now let's adjust the pose!</Card.Text>
        <PoseModal uuid={uuid} />
      </Card.Body>
      <Card.Footer className="text-muted">
        <Button variant="secondary">Done</Button>
      </Card.Footer>
    </Card>
  );
};

const PoseModal = ({ uuid }: Props) => {
  const [isLoading, setIsLoading] = useState(true);
  const [pose, setPose] = useState<object>();
  const [imageUrl, setImageUrl] = useState<any>();

  useEffect(() => {
    const loadPose = async () => {
      setIsLoading(true);

      try {
        const form = new FormData();
        if (uuid) {
          form.set("uuid", uuid);
        }

        const result = await axios.post(
          "http://localhost:5000/get_joint_locations_json",
          form,
          {
            timeout: 30000,
            headers: {
              "Content-Type": "multipart/form-data",
            }, // 30s timeout
          }
        );

        const imageResult = await axios.post(
          "http://localhost:5000/get_cropped_image",
          form,
          {
            timeout: 30000,
            responseType: "blob",
            headers: {
              "Content-Type": "multipart/form-data",
            }, // 30s timeout
          }
        );

        // TODO handle uploaded image
        // console.log(result);
        setPose(result.data);
        let reader = new window.FileReader();
        reader.readAsDataURL(imageResult.data);
        reader.onload = function () {
          let imageDataUrl = reader.result;
          //console.log(imageDataUrl);
          setImageUrl(imageDataUrl);
        };
      } catch (error) {
        console.log(error);
        // onError(error);
      } finally {
        setIsLoading(false);
      }
    };

    loadPose();
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
      {startPose && <PoseEditor imageUrl={imageUrl} startPose={startPose} />}
    </>
  );
};

export default PoseModal;
