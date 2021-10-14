import React from "react";

interface props {
  drawingURL: string;
  showText?: boolean;
}

const Loader = ({ drawingURL, showText }: props) => {
  return (
    <div className="custom-loader">
      {drawingURL !== "" ? <img src={drawingURL} alt="drawing" /> : null}
      {showText && <p>Your animation should be ready soon!</p>}
      <svg width="100%" height="100%" viewBox="0 0 200 200">
        <rect x="0" y="0" width="100%" height="4" fill="#3D92C7">
          <animate
            attributeName="y"
            from="0"
            to="200"
            dur="1.5s"
            repeatCount="indefinite"
          />
        </rect>
      </svg>
    </div>
  );
};

export default Loader;
