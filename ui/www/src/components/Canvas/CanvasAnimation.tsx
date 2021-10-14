import React, { useEffect, useState } from "react";
import { useLocation } from "react-router";
import { Row, Col, Button, Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import Loader from "../Loader";
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
  const { isLoading, getAnimation } = useDrawingApi((err) => {
    console.log(err);
  });
  const location = useLocation();
  const [showModal, setModal] = useState(false);

  /**
   * When the CanvasAnimation component mounts, invokes the API to get an animation
   * given the current uuid and animationType params.
   * The component will only rerender when the uuid or animationType dependency changes.
   * exhaustive-deps eslint warning is disable as no more dependencies are really necesary as side effects.
   * In contrast, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchAnimation = async () => {
      setRenderingVideo(true)
      await getAnimation(uuid, animationType, (data) => {
        loadVideoBlob(data as string);
      });
      setRenderingVideo(false)
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
              // TODO Show Error.
              throw e;
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

      var filesArray: File[] = [
        new File([data], "animation.mp4", {
          type: "video/mp4",
          lastModified: Date.now(),
        }),
      ];

      var blob = new Blob([data], { type: "video/mp4" });
      setVideoDownload(URL.createObjectURL(blob));
      setAnimationFiles(filesArray);
      reader.readAsDataURL(blob);
    }
  };

  const handleShare = () => {
    let data = {
      url: `${window.location.href}${location.search}`,
      title: "Animation",
      text: "Check this kid's drawing animation",
      files: animationFiles,
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
    const videoPlayer = document.getElementById("videoPlayer") as HTMLVideoElement;
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
                <>
                  Download
                </>
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
