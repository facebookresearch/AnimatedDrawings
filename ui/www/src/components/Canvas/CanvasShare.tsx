import React, { useEffect, useState, forwardRef } from "react";
import { useLocation, useHistory } from "react-router";
import { Dropdown, Spinner, Alert } from "react-bootstrap";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import ShareModal from "../Modals/ShareModal";

interface Props {
  uuid: string;
  animationType: string;
}

const CustomToggle = forwardRef(({ children, onClick }: any, ref: any) => (
  <a
    href="/#"
    ref={ref}
    onClick={(e) => {
      e.preventDefault();
      onClick(e);
    }}
  >
    {children}
  </a>
));

const CanvasShare = ({ uuid, animationType }: Props) => {
  const { isLoading, getAnimation } = useDrawingApi((err) => {
    console.log(err);
  });
  const location = useLocation();
  const history = useHistory();
  const [animationFiles, setAnimationFiles] = useState<File[]>([]);
  const [videoDownload, setVideoDownload] = useState("");
  const [showModal, setModal] = useState(false);
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
    let shareLink = `${window.location.href}${location.search}`;
    return shareLink;
  };

  return (
    <div className="canvas-wrapper">
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
      <div className="text-right m-2">
        <Dropdown className="d-inline mx-2" drop="up">
          <Dropdown.Toggle as={CustomToggle} id="dropdown-autoclose-true">
            <i className="bi bi-three-dots h1 text-dark" />
          </Dropdown.Toggle>

          <Dropdown.Menu>
            <Dropdown.Item
              download="animation.mp4"
              href={videoDownload}
              target="_blank"
              rel="noreferrer"
            >
              {" "}
              <i className="bi bi-download mr-2" /> Download
            </Dropdown.Item>
            <Dropdown.Item onClick={handleShare}>
              {" "}
              <i className="bi bi-share-fill mr-2" /> Share
            </Dropdown.Item>
            <Dropdown.Item href="#" className="text-danger">
              <i className="bi bi-flag-fill text-danger mr-2" /> Report
            </Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>
      <div className="canvas-background border border-dark">
        {isLoading ? (
          <Spinner animation="border" role="status" aria-hidden="true" />
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
          <button
            className="md-button-2 border border-dark"
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
                <i className="bi bi-download" /> Download
              </>
            )}
          </button>
        </a>

        <button
          className="md-button border border-dark"
          disabled={isLoading}
          onClick={handleShare}
        >
          <i className="bi bi-share-fill" /> Share
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

export default CanvasShare;
