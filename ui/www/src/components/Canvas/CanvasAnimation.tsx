import React, { useEffect, useState } from "react";
import { useLocation } from "react-router";
import { Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import Loader from "../Loader";
import ShareModal from "../Modals/ShareModal";

const CanvasAnimation = () => {
  const {
    uuid,
    drawing,
    videoDownload,
    animationType,
    animationFiles,
    setVideoDownload,
    setAnimationFiles,
  } = useDrawingStore();
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
      await getAnimation(uuid, animationType, (data) => {
        loadVideoBlob(data as string);
      });
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
    let shareLink = `${window.location.href}share/${uuid}/${animationType}`;
    return shareLink;
  };

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {isLoading ? (
          <Loader drawingURL={drawing} />
        ) : (
          <div className="video_box">
            <video id="videoPlayer" autoPlay muted loop></video>
          </div>
        )}
      </div>

      <div className="mt-3 text-center">
        <a
          download="animation.mp4"
          href={videoDownload}
          target="_blank"
          rel="noreferrer"
        >
          <button className="buttons md-button mr-1" disabled={isLoading}>
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
                <i className="bi bi-download mr-2" /> Download
              </>
            )}
          </button>
        </a>

        <button
          className="buttons md-button ml-1"
          disabled={isLoading}
          onClick={handleShare}
        >
          <i className="bi bi-share-fill mr-2" /> Share
        </button>
      </div>
      <ShareModal
        showModal={showModal}
        handleModal={() => setModal(!showModal)}
        title={"Share"}
        getShareLink={getShareLink}
      />
    </div>
  );
};

export default CanvasAnimation;
