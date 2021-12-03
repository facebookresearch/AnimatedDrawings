import React, { useEffect, useState } from "react";
import { useHistory } from "react-router";
import { Row, Col, Button, Spinner, Alert } from "react-bootstrap";
import { useDrawingApi } from "../../hooks/useDrawingApi";

const VIDEO_URL = window._env_.VIDEO_URL;

interface Props {
  videoId: string;
  animationType: string;
}

const CanvasShare = ({ videoId, animationType }: Props) => {
  const { isLoading, getAnimation } = useDrawingApi((err) => {
    console.log(err);
  });
  const history = useHistory();
  const [videoDownload, setVideoDownload] = useState("");
  const [showWarning, setShowWarning] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>();

  /**
   * When the CanvasAnimation component mounts, invokes the API to get an animation
   * given a videoId and animationType params.
   * The component will only rerender when the videoId or animationType dependency changes.
   * exhaustive-deps eslint warning is disable as no more dependencies are really necesary as side effects.
   * In contrast, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchAnimation = async () => {
      try {
        setVideoUrl(`${VIDEO_URL}/${videoId}/${animationType}.mp4`);
      } catch (error) {
        console.log(error);
        setShowWarning(true);
      }
    };
    fetchAnimation();
    return () => {};
  }, [videoId, animationType]); // eslint-disable-line react-hooks/exhaustive-deps

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
            link is broken or the content is no longer available. You can still make your own animation.
          </Alert.Heading>
        </Alert>
      )}
      <div className="canvas-background">
        {isLoading ? (
          <Spinner animation="border" role="status" aria-hidden="true" />
        ) : (
          <div className="video_box">
            <video id="videoPlayer" autoPlay muted loop src={videoUrl}></video>
          </div>
        )}
      </div>

      <Row className="justify-content-center mt-3">
        <Col lg={6} md={6} xs={12}>
          <Button
            block
            size="lg"
            variant="primary"
            className="py-lg-3 mt-lg-3 my-1"
            href="/"
          >
            Create your Animation
          </Button>
        </Col>
        <Col lg={6} md={6} xs={12} className="text-center">
          <a
            download="animation.mp4"
            href={videoDownload} // TODO Figure out how to download the video. Maybe a direct download
            target="_blank"
            rel="noreferrer"
          >
            <Button
              block
              size="lg"
              variant="info"
              className="py-lg-3 mt-lg-3 my-1 text-primary"
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
