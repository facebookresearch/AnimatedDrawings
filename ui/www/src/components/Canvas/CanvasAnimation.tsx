import React, { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router";
import { Row, Col, Button, Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import { Loader } from "../Loader";
import ShareModal from "../Modals/ShareModal";

declare global {
  interface Element {
    requestFullScreen?(): void /* W3C API */;
    webkitRequestFullScreen?(): void /* Chrome, Opera - Webkit API */;
    mozRequestFullScreen?(): void /* Firefox */;
    webkitEnterFullScreen?(): void /* Safari on iOs */;
  }
}

const CanvasAnimation = () => {
  const {
    uuid,
    videoDownload,
    animationType,
    animationFiles,
    setRenderingVideo,
    setVideoDownload,
    setAnimationFiles,
  } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();
  const errorHandler = useCallback((err) => {
    console.log(err);
  }, []);
  const { isLoading, getAnimation } = useDrawingApi(errorHandler);
  const location = useLocation();
  const [showModal, setModal] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>();

  /**
   * When the CanvasAnimation component mounts, invokes the API to get an animation
   * given the current uuid and animationType params.
   * The component will only rerender when the uuid or animationType dependency changes.
   * exhaustive-deps eslint warning is disable as no more dependencies are really necesary as side effects.
   * In contrast, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchAnimation = async () => {
      setRenderingVideo(true);
      setVideoUrl("");
      await getAnimation(uuid, animationType, (data) => {
        let videoId = data as string;
        setVideoUrl(
          `http://localhost:5000/video/${videoId}/${animationType}.mp4`
        );
      });
      setRenderingVideo(false);
    };
    fetchAnimation();
    return () => {};
  }, [uuid, animationType]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleShare = () => {
    let data = {
      url: `${window.location.href}${location.search}`,
      title: "Animation",
      text: "Check this kid's drawing animation",
      files: animationFiles, // TODO Looks like we're sharing the downloaded file here. Need to check if it works for a URL. If not we may need to download the video first.
    };
    if (
      typeof navigator.share === "function"
      //&& navigator.canShare({ files: animationFile })
    ) {
      navigator
        .share(data)
        .then(() => console.log("Successful share"))
        .catch((error) => console.log("Error sharing", error));
    } else {
      console.log("Your device does not support sharing");
      setModal(true);
    }
  };

  const getShareLink = () => {
    let shareLink = `${window.location.origin}/share/${uuid}/${animationType}`;
    return shareLink;
  };

  // Create fullscreen video
  const toggleFullScreen = () => {
    const videoPlayer = document.getElementById(
      "videoPlayer"
    ) as HTMLVideoElement;
    if (videoPlayer && videoPlayer.requestFullScreen) {
      videoPlayer.requestFullScreen();
    } else if (videoPlayer && videoPlayer.webkitRequestFullScreen) {
      videoPlayer.webkitRequestFullScreen();
    } else if (videoPlayer && videoPlayer.mozRequestFullScreen) {
      videoPlayer.mozRequestFullScreen();
    } else if (videoPlayer && videoPlayer.webkitEnterFullScreen) {
      videoPlayer.webkitEnterFullScreen(); // IOS Mobile edge case
    }
  };

  return (
    <div className="canvas-wrapper">
      <div className="blue-box d-none d-lg-block"></div>
      <div className="canvas-background-p-0">
        {isLoading ? (
          <Loader drawingURL={""} showText />
        ) : (
          <div className="video_box">
            <video
              id="videoPlayer"
              autoPlay
              muted
              loop
              playsInline
              src={videoUrl}
            ></video>
            <div className="custom-controls">
              <div className="fullscreen-btn" onClick={toggleFullScreen}>
                <i className="bi bi-arrows-fullscreen text-dark h3" />
              </div>
            </div>
          </div>
        )}
      </div>

      <Row className="justify-content-center mt-3">
        <Col lg={2} md={2} xs={3}>
          <Button
            block
            size="lg"
            variant="outline-primary"
            className="py-lg-3 mt-lg-3 my-1"
            onClick={() => setCurrentStep(currentStep - 1)}
          >
            Fix
          </Button>
        </Col>
        <Col lg={5} md={5} xs={4}>
          <Button
            block
            size="lg"
            className="py-3 mt-3 d-none d-lg-block shadow-button"
            disabled={isLoading}
            href="/canvas"
          >
            Create new drawing
          </Button>
          <a
            download="animation.mp4"
            href={videoDownload}
            target="_blank"
            rel="noreferrer"
          >
            <Button
              block
              size="lg"
              className="py-lg-3 mt-lg-3 my-1 d-inline-block d-none d-sm-none"
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
                <>Download</>
              )}
            </Button>
          </a>
        </Col>
        <Col lg={5} md={5} xs={4}>
          <Button
            block
            size="lg"
            variant="info"
            className="py-lg-3 mt-lg-3 my-1 px-0 text-primary shadow-button"
            disabled={isLoading}
            onClick={handleShare}
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
                <i className="bi bi-share-fill mr-1" /> Share
              </>
            )}
          </Button>
        </Col>
      </Row>
      <ShareModal
        showModal={showModal}
        handleModal={() => setModal(!showModal)}
        title={"SHARE"}
        getShareLink={getShareLink}
        videoDownload={videoDownload}
      />
    </div>
  );
};

export default CanvasAnimation;
