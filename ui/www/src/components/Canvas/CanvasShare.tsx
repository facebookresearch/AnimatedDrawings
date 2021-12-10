import React, { useEffect, useState } from "react";
import { useHistory } from "react-router";
import { Row, Col, Button, Spinner, Alert } from "react-bootstrap";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import ShareModal from "../Modals/ShareModal";
import ShareIcon from "../../assets/customIcons/nav_share.svg";

const VIDEO_URL = window._env_.VIDEO_URL;

interface Props {
  videoId: string;
  animationType: string;
}

const CanvasShare = ({ videoId, animationType }: Props) => {
  const { isLoading, getVideoFile } = useDrawingApi((err) => {
    console.log(err);
  });
  const history = useHistory();
  const [videoDownload, setVideoDownload] = useState("");
  const [animationFiles, setAnimationFiles] = useState<File[]>([]);
  const [showWarning, setShowWarning] = useState(false);
  const [showModal, setModal] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>();

  /**
   * When the CanvasShare component mounts, invokes the API to get an animation
   * given a videoId and animationType params.
   * The component will only rerender when the videoId or animationType dependency changes.
   * exhaustive-deps eslint warning is disable as no more dependencies are really necesary as side effects.
   * In contrast, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchAnimation = async () => {
      try {
        await getVideoFile(videoId, animationType, (data) => {
          let reader = new window.FileReader();
          reader.readAsDataURL(data);
          reader.onload = function () {
            let videoDataUrl = reader.result as string;
            setVideoDownload(videoDataUrl);
          };
          setShareableFile(data);
        });

        setVideoUrl(`${VIDEO_URL}/${videoId}/${animationType}.mp4`);
      } catch (error) {
        console.log(error);
        setShowWarning(true);
      }
    };
    fetchAnimation();
    return () => {};
  }, [videoId, animationType]); // eslint-disable-line react-hooks/exhaustive-deps

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
    videoPlayer.play()
  }

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
            link is broken or the content is no longer available. You can still
            make your own animation.
          </Alert.Heading>
        </Alert>
      )}
      <div className="canvas-background">
        {isLoading ? (
          <Spinner animation="border" role="status" aria-hidden="true" />
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
            <div className="replay-wrapper" onClick={playVideo}/>
            <div className="custom-controls">
              <div className="fullscreen-btn" onClick={toggleFullScreen}>
                <i className="bi bi-arrows-fullscreen text-dark h3" />
              </div>
            </div>
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
          <Button
            block
            size="lg"
            variant="info"
            className="py-lg-3 mt-lg-3 my-1 text-primary"
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
                <img
                  src={ShareIcon}
                  alt=""
                  className="mr-1"
                />
                Share
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
};;

export default CanvasShare;
