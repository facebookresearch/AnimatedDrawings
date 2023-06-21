//  Copyright (c) Meta Platforms, Inc. and affiliates.
//  This source code is licensed under the MIT license found in the
//  LICENSE file in the root directory of this source tree.

import React from "react";

import Circle from "./Pose/Circle";
import Line from "./Pose/Line";

export default function App() {
  // grab global vars inserted by the Flask app
  const cfg = window.cfg;
  const imageData = window.image.data; 

  const imageHeight = cfg.height;
  const imageWidth = cfg.width;
  const originalPoints = cfg.skeleton;

  const [points, setPoints] = React.useState(() =>
    JSON.parse(JSON.stringify(originalPoints))
  );
  const [hoveredJoint, setHoveredJoint] = React.useState(null);
  const [isMoving, setIsMoving] = React.useState(false);

  return (
    <>
      <div style={{ position: "relative", height: imageHeight }}>
        <div style={{ position: "absolute" }}>
          <img
            src={"data:image/png;base64," + imageData}
            style={{ height: imageHeight, width: imageWidth }}
          />
        </div>
        <div style={{ position: "absolute" }}>
          <svg
            style={{ width: imageWidth, height: imageHeight }}
            viewBox={`0 0 ${imageWidth} ${imageHeight}`}
            xmlns="http://www.w3.org/2000/svg"
          >
            {points.map((pt) => {
              if (!pt.parent) return;
              let parent = points.find((p) => p.name === pt.parent);

              return (
                <Line
                  key={`${pt.name}-${pt.parent}`}
                  x1={pt.loc[0]}
                  y1={pt.loc[1]}
                  x2={parent.loc[0]}
                  y2={parent.loc[1]}
                  isActive={
                    isMoving && [pt.name, pt.parent].indexOf(hoveredJoint) >= 0
                  }
                />
              );
            })}
            {points.map((pt) => (
              <Circle
                key={pt.name}
                cx={pt.loc[0]}
                cy={pt.loc[1]}
                xBounds={[0, imageWidth]}
                yBounds={[0, imageHeight]}
                onPositionUpdate={(pos) => {
                  const newPos = [pos.x, pos.y];
                  const newPts = points.map((p) =>
                    p.name !== pt.name ? p : { ...p, loc: newPos }
                  );
                  setPoints(newPts);
                  setIsMoving(pos.active);
                }}
                onHover={(enter) => {
                  setHoveredJoint(enter ? pt.name : null);
                }}
                strokeWidth="2"
                stroke="white"
                r="4"
              />
            ))}
          </svg>
          {hoveredJoint ? (
            <div className="tooltip">
              {hoveredJoint?.replace("l_", "left ")?.replace("r_", "right ")}
            </div>
          ) : null}
        </div>
      </div>
      <form method="POST" action="/annotations/submit">
        <input
          hidden={true}
          type="text"
          value={JSON.stringify({ ...cfg, skeleton: points })}
          id="data"
          name="data"
        />
        <button type="submit">Submit</button>
      </form>
    </>
  );
}
