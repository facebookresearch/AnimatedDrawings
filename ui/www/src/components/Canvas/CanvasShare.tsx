import React, { useEffect, useState } from "react";
import { useHistory } from "react-router";
import { Row, Col, Button, Spinner, Alert } from "react-bootstrap";
import { useDrawingApi } from "../../hooks/useDrawingApi";

interface Props {
  uuid: string;
  animationType: string;
}

const CanvasShare = ({ uuid, animationType }: Props) => {
  const { isLoading, getAnimation } = useDrawingApi((err) => {
    console.log(err);
  });
  const history = useHistory();
  const [videoDownload, setVideoDownload] = useState("");
  const [showWarning, setShowWarning] = useState(false);

  /**
   * When the CanvasAnimation component mounts, invokes the API to get an animation
   * given the current uuid and animationType params.
   * The component will only rerender when the uuid or animationType dependency changes.
   * exhaustive-deps eslint warning is disable as no more dependencies are really necesary as side effects.
   * In contrast, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchAnimation = async () => {
      try {
        await getAnimation(uuid, animationType, (data) => {
          loadVideoBlob(data as string);
        });
      } catch (error) {
        console.log(error);
        setShowWarning(true);
      }
    };
    fetchAnimation();
    return () => {};
  }, [uuid, animationType]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadVideoBlob = (data: string) => {
    var reader = new FileReader();

    if (data !== null && data !== undefined) {
      reader.onload = (e) => {
        const dataUrl = e.target?.result;
        if (dataUrl && typeof dataUrl === "string") {
          const videoPlayer = document.getElementById("videoPlayer");

          if (videoPlayer && videoPlayer instanceof HTMLVideoElement) {
            videoPlayer.onerror = (e) => {
              debugger;
              console.log("Error in Video Player", e, videoPlayer.error);
              setShowWarning(true);
            };
            videoPlayer.src = dataUrl;
            videoPlayer.loop = true;
            videoPlayer.load();
            videoPlayer.onloadeddata = function () {
              videoPlayer.play();
            };
          }
        }
      };

      var blob = new Blob([data], { type: "video/mp4" });
      setVideoDownload(URL.createObjectURL(blob));
      reader.readAsDataURL(blob);
    }
  };

  return (
    <div className="canvas-wrapper">
      <div className="blue-box d-none d-lg-block"></div>
      {showWarning && (
        <Alert
          variant="danger"
          className="mt-2"
          dismissible
          onClose={() => history.push("/")}
        >
          <Alert.Heading>
            <span className="text-weight">Oh snap!</span> You got an error, this
            link is broken. You can still make your own animation.
          </Alert.Heading>
        </Alert>
      )}
      <div className="canvas-background">
        {isLoading ? (
          <Spinner animation="border" role="status" aria-hidden="true" />
        ) : (
          <div className="video_box">
            <video id="videoPlayer" autoPlay muted loop></video>
          </div>
        )}
      </div>

      <Row className="justify-content-center mt-3">
        <Col lg={6} md={6} xs={12}>
          <Button block size="lg" variant="primary" className="my-1" href="/">
            Create your Animation
          </Button>
        </Col>
        <Col lg={6} md={6} xs={12} className="text-center">
          <a
            download="animation.mp4"
            href={videoDownload}
            target="_blank"
            rel="noreferrer"
          >
            <Button
              block
              size="lg"
              variant="info"
              className="my-1 text-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />
              ) : (
                <>
                  <i className="bi bi-download mr-1" /> Download
                </>
              )}
            </Button>
          </a>
        </Col>
      </Row>
    </div>
  );
};

export default CanvasShare;
