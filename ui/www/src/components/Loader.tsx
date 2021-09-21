import React from "react";

interface props {
  drawingURL: string;
}

const Loader = ({ drawingURL }: props) => {
  return (
    <div className="custom-loader">
      <img src={drawingURL} alt="drawing" />
      <svg width="100%" height="100%" viewBox="0 0 200 200">
        <rect x="0" y="0" width="100%" height="5" fill="#FEB1C8">
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
