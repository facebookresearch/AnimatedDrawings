import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useDrawingApi } from "../hooks/useDrawingApi";

interface Props {
  // uuid?: string;
}

const ResultsPage = (params: Props) => {
  const { uuid } = useParams<{ uuid: string }>();
  const [videoData, setVideoData] = useState<string>();
  const { isLoading, getAnimation } = useDrawingApi((err) => {});

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
    getAnimation(uuid, (data) => {
      loadVideoBlob(data as string);
    });
    return () => {};
  }, [uuid]);

  return (
    <div>
      <video
        id="videoPlayer"
        autoPlay
        muted
        loop
        className="min-vh-100 position-absolute"
      ></video>
    </div>
  );
};

export default ResultsPage;
