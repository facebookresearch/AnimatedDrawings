import React from "react";

interface props {
  drawingURL: string;
  showText?: boolean;
}

export const EmptyLoader = () => {
  return (
    <svg width="100%" height="100%" viewBox="0 0 200 200">
      <rect x="0" y="0" width="100%" height="4" fill="#3D92C7">
        <animate
          attributeName="y"
          values="10;190;10"
          dur="3s"
          repeatCount="indefinite"
        />
      </rect>
    </svg>
  );
};

export const Loader = ({ drawingURL, showText }: props) => {
  return (
    <div className="custom-loader">   
      {showText && <div className="text-background">Your animation should be ready soon!</div>}
      <svg width="100%" height="100%" viewBox="0 0 200 200">
        <image href={drawingURL} height="100%" width="100%" preserveAspectRatio="xMidYMid meet"/>
        {drawingURL !== "" ? <image href={drawingURL} height="100%" width="100%"/> : null}
        <rect x="0" y="0" width="100%" height="4" fill="#3D92C7">
          <animate
            attributeName="y"
            values="10;190;10"
            dur="3s"
            repeatCount="indefinite"
          />
        </rect>
      </svg>
    </div>
  );
};
