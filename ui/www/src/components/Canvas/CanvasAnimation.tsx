import React, { useCallback, useEffect, useState } from "react";
import { Row, Col, Button, Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import { Loader } from "../Loader";
import ShareModal from "../Modals/ShareModal";
import ShareIcon from "../../assets/customIcons/nav_share.svg";
import useLogPageView from "../../hooks/useLogPageView";
import { isFromScenes } from "../../utils/Scenes";
import ScenesDoneButton from "../Scenes/ScenesDoneButton";

const VIDEO_URL = window._env_.VIDEO_URL;

declare global {
  interface Element {
    requestFullScreen?(): void /* W3C API */;
    webkitRequestFullScreen?(): void /* Chrome, Opera - Webkit API */;
    mozRequestFullScreen?(): void /* Firefox */;
    webkitEnterFullScreen?(): void /* Safari on iOs */;
  }
}

const CanvasAnimation = () => {
  useLogPageView("Animation", "#animate");
  const { uuid, animationType, setRenderingVideo } = useDrawingStore();
  const { currentStep, setError, setCurrentStep } = useStepperStore();

  const errorHandler = useCallback(
    (err) => {
      let isSubscribed = true;
      if (isSubscribed) {
        setError(err.response.status);
        console.log(err);
      }

      return () => {
        isSubscribed = false;
      };
    },
    [setError]
  );

  const { isLoading, getAnimation, getVideoFile } = useDrawingApi(errorHandler);
  const [videoDownload, setVideoDownload] = useState("");
  const [animationFiles, setAnimationFiles] = useState<File[]>([]);
  const [showModal, setModal] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [videoId, setVideoId] = useState<string>("");
  const [webpUrl, setWebpUrl] = useState<string>();

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
        setRenderingVideo(true);
        setVideoUrl("");

        await getAnimation(uuid, animationType, isFromScenes, (data) => {
          setVideoId(data as string);
          setVideoUrl(`${VIDEO_URL}/${data as string}/${animationType}.mp4`);
          if (isFromScenes) {
            setWebpUrl(`${VIDEO_URL}/${data as string}/${animationType}.webp`);
          }
          // Get the video file to share and download.
          getVideoFile(data, animationType, (data) => {
            let reader = new window.FileReader();
            reader.readAsDataURL(data);
            reader.onload = function () {
              let videoDataUrl = reader.result as string;
              setVideoDownload(videoDataUrl);
            };
            setShareableFile(data);
          });
        });

        setRenderingVideo(false);
      } catch (error) {
        console.log(error);
      }
    };

    fetchAnimation();
    return () => { };
  }, [uuid, animationType]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Updates the animationFiles state as an array of files, required for he navigator share API.
   * @param data video blob
   */
  const setShareableFile = (data: string) => {
    let filesArray: File[] = [
      new File([data], "animation.mp4", {
        type: "video/mp4",
        lastModified: Date.now(),
      }),
    ];
    setAnimationFiles(filesArray);
  };

  const handleShare = () => {
    let data = {
      url: `${window.location.origin}/share/${videoId}/${animationType}`,
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
      // Use the share modal when on desktop.
      setModal(true);
    }
  };

  const getShareLink = () => {
    let shareLink = `${window.location.origin}/share/${videoId}/${animationType}`;
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

  /**
   * Play function, to be called when clicking or taping on canvas,
   * fallback for browsers that don't support autoplay.
   */
  const playVideo = () => {
    const videoPlayer = document.getElementById(
      "videoPlayer"
    ) as HTMLVideoElement;
    videoPlayer.play();
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
              autoPlay={!isFromScenes}
              muted
              loop
              playsInline
              src={videoUrl}
            ></video>
            <div className="replay-wrapper" onClick={playVideo} />
            <div className="custom-controls">
              <div className="fullscreen-btn" onClick={toggleFullScreen}>
                <i className="bi bi-arrows-fullscreen text-dark h3" />
              </div>
            </div>
          </div>
        )}
      </div>
      {!isFromScenes ? (
        <Row className="justify-content-center mt-3 px-1 pb-1">
          <Col lg={4} md={4} xs={4} className="px-2">
            <Button
              block
              size="lg"
              className="py-lg-3 mt-lg-3 my-1 px-0 shadow-button"
              disabled={isLoading}
              href="/canvas"
            >
              <i className="bi bi-plus-lg mr-lg-2" /> Drawing
            </Button>
          </Col>
          <Col lg={4} md={4} xs={4} className="px-2">
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
                  <img src={ShareIcon} alt="" className="mr-1" /> Share
                </>
              )}
            </Button>
          </Col>
          <Col lg={4} md={4} xs={4} className="px-2">
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
        </Row>
      ) : <ScenesDoneButton isLoading={isLoading} webPUrl={webpUrl} />}
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
