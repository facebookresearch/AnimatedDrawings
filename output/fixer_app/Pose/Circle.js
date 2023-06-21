// Copyright (c) Meta Platforms, Inc. and affiliates.
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.

import React from "react";

const Circle = ({
  cx,
  cy,
  xBounds = [-Infinity, Infinity],
  yBounds = [-Infinity, Infinity],
  onPositionUpdate,
  onHover,
  ...props
}) => {
  // credit: https://gist.github.com/hashrock/0e8f10d9a233127c5e33b09ca6883ff4
  //
  const [position, setPositionRaw] = React.useState({
    x: cx,
    y: cy,
    active: false,
    offset: {},
  });

  let [minX, maxX] = xBounds;
  let [minY, maxY] = yBounds;

  const setPosition = React.useCallback(
    (pos) => {
      onPositionUpdate(pos);
      setPositionRaw(pos);
    },
    [setPositionRaw, onPositionUpdate]
  );

  const handlePointerDown = (e) => {
    const el = e.target;
    const bbox = e.target.getBoundingClientRect();
    const x = e.clientX - bbox.left;
    const y = e.clientY - bbox.top;
    el.setPointerCapture(e.pointerId);
    setPosition({
      ...position,
      active: true,
      offset: {
        x: Math.min(Math.max(x, minX), maxX),
        y: Math.min(Math.max(y, minY), maxY),
      },
    });
  };
  const handlePointerMove = (e) => {
    const bbox = e.target.getBoundingClientRect();
    const x = e.clientX - bbox.left;
    const y = e.clientY - bbox.top;
    const newX = position.x - (position.offset.x - x);
    const newY = position.y - (position.offset.y - y);
    const movePosition = {
      ...position,
      x: Math.min(Math.max(newX, minX), maxX),
      y: Math.min(Math.max(newY, minY), maxY),
    };
    if (position.active) {
      setPosition(movePosition);
    }
  };
  const handlePointerEnter = () => {
    onHover(true);
  };
  const handlePointerLeave = () => {
    onHover(false);
  };
  const handlePointerUp = (e) => {
    setPosition({
      ...position,
      active: false,
    });
  };

  return (
    <circle
      cx={position.x}
      cy={position.y}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerMove={handlePointerMove}
      onPointerOut={handlePointerLeave}
      onPointerEnter={handlePointerEnter}
      {...props}
      fill={position.active ? "red" : "#aaa"}
    />
  );
};

export default Circle;
