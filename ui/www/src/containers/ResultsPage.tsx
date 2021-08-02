import React, { useEffect, useState } from "react";
import { Col, Container, Dropdown, Row, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { useDrawingApi } from "../hooks/useDrawingApi";

interface Props {
  // uuid?: string;
}

enum AnimationType {
  RunJump = "run_jump",
  Wave = "wave",
  Dance = "dance",
}

const ResultsPage = (params: Props) => {
  const { uuid } = useParams<{ uuid: string }>();
  const [animationType, setAnimationType] = useState<AnimationType>(
    AnimationType.RunJump
  );
  const { isLoading, getAnimation } = useDrawingApi((err) => {
    console.log(err);
  });

  function loadVideoBlob(data: string) {
    var reader = new FileReader();

    if (data !== null && data !== undefined) {
      reader.onload = (e) => {
        const dataUrl = e.target?.result;
        if (dataUrl && typeof dataUrl === "string") {
          console.log(dataUrl);

          const videoPlayer = document.getElementById("videoPlayer");

          if (videoPlayer && videoPlayer instanceof HTMLVideoElement) {
            videoPlayer.onerror = (e) => {
              debugger;
              console.log("Error in Video Player", e, videoPlayer.error);
              // TODO Show Error.
              throw e;
            };
            videoPlayer.src = dataUrl;
            videoPlayer.loop = true;
            videoPlayer.load();
            videoPlayer.onloadeddata = function () {
              videoPlayer.play();
              // setIsLoading(false);
            };
          }
        }
      };

      var blob = new Blob([data], { type: "video/mp4" });
      reader.readAsDataURL(blob);
    }
  }

  useEffect(() => {
    getAnimation(uuid, animationType, (data) => {
      loadVideoBlob(data as string);
    });
    return () => {};
  }, [uuid, animationType]);

  return (
    <div>
      <video
        id="videoPlayer"
        autoPlay
        muted
        loop
        className="min-vh-100 position-absolute"
      ></video>
      <Container fluid>
        <Row noGutters={true} className="vh-100">
          {isLoading && (
            <Spinner
              animation="border"
              role="status"
              aria-hidden="true"
              className=" position-fixed align-middle"
            />
          )}
          <Col className="d-flex flex-row justify-content-end vh-100">
            <Dropdown className="m-3">
              <Dropdown.Toggle variant="success" id="dropdown-basic">
                Animation
              </Dropdown.Toggle>

              <Dropdown.Menu onSelect={(key, e) => console.log(key, e)}>
                <Dropdown.Item
                  onSelect={() => setAnimationType(AnimationType.RunJump)}
                >
                  Run Jump
                </Dropdown.Item>
                <Dropdown.Item
                  onSelect={() => setAnimationType(AnimationType.Wave)}
                >
                  Wave
                </Dropdown.Item>
                <Dropdown.Item
                  onSelect={() => setAnimationType(AnimationType.Dance)}
                >
                  Dance
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default ResultsPage;
