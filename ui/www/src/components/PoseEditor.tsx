import React, { useEffect, useState } from "react";

export interface Position {
  x: number;
  y: number;
}

interface PoseNode {
  id: string;
  label: string;
  position: Position;
}

interface PoseEdge {
  from: string;
  to: string;
}

export interface Pose {
  nodes: Array<PoseNode>;
  edges: Array<PoseEdge>;
}

interface Props {
  //   imageHeight: number;
  //   imageWidth: number;
  imageUrl: any;
  maskUrl: any;
  pose: Pose;
  isLoading?: boolean;
  scale: number;
  setPose: (pose: Pose) => void;
}

interface LineProps extends React.SVGProps<SVGLineElement> {}
const Line = (props: LineProps) => {
  return <line {...props} />;
};

interface CircleProps extends React.SVGProps<SVGCircleElement> {
  cx: number;
  cy: number;
  imgWidth: number;
  imgHeight: number;
  onPositionUpdate: (position: CirclePosition) => void;
  onHover: (hover: boolean) => void;
}

interface CirclePosition extends Position {
  active: false;
  offset: Position;
}
const Circle = ({
  cx,
  cy,
  imgWidth,
  imgHeight,
  onPositionUpdate,
  onHover,
  ...props
}: CircleProps) => {
  // credit: https://gist.github.com/hashrock/0e8f10d9a233127c5e33b09ca6883ff4
  const [position, setPositionRaw] = React.useState<CirclePosition>({
    x: cx,
    y: cy,
    active: false,
    offset: {
      x: 0,
      y: 0,
    },
  });

  const setPosition = React.useCallback(
    (pos) => {
      onPositionUpdate(pos);
      setPositionRaw(pos);
    },
    [setPositionRaw, onPositionUpdate]
  );
  const handlePointerDown = (e: React.PointerEvent<SVGCircleElement>) => {
    const el = (e.target as Element)!;
    const bbox = (e.target as Element)!.getBoundingClientRect();
    const x = e.clientX - bbox.left;
    const y = e.clientY - bbox.top;
    el.setPointerCapture(e.pointerId);
    setPosition({
      ...position,
      active: true,
      offset: {
        x,
        y,
      },
    });
  };
  const handlePointerMove = (e: React.PointerEvent<SVGCircleElement>) => {
    const bbox = (e.target! as Element)!.getBoundingClientRect();
    const x = e.clientX - bbox.left;
    const y = e.clientY - bbox.top;
    const movePosition = {
      ...position,
      x: position.x - (position.offset.x - x),
      y: position.y - (position.offset.y - y),
    };
    if (
      position.active &&
      movePosition.x > 0 &&
      movePosition.y > 0 &&
      movePosition.x < imgWidth &&
      movePosition.y < imgHeight
    ) {
      setPosition(movePosition);
    }
  };
  const handlePointerEnter = () => {
    onHover(true);
  };
  const handlePointerLeave = () => {
    onHover(false);
  };
  const handlePointerUp = (e: React.PointerEvent<SVGCircleElement>) => {
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

const PoseEditor = ({ imageUrl, maskUrl, pose, scale, isLoading, setPose }: Props) => {
  const [hoveredJoint, setHoveredJoint] = React.useState<string>();
  const [isMoving, setIsMoving] = React.useState(false);

  const [imageWidth, setImageWidth] = useState(0);
  const [imageHeight, setImageHeight] = useState(0);

  //const [debug, setDebug] = useState(true);
  //const padding = 20;
  //const yStep = (imageHeight - padding) / 7;
  //const xStep = (imageWidth - padding) / 8;
  const mapX = (unit: number) => unit; // * xStep + imageWidth / 2;
  const mapY = (unit: number) => unit; // * yStep + padding;
  const unmapX = (coord: number) => coord; //(coord - imageWidth / 2) / xStep;
  const unmapY = (coord: number) => coord; //(coord - padding) / yStep;

  const nodeMap = pose.nodes.reduce((map, entry) => {
    map.set(entry.id, entry);
    return map;
  }, new Map<string, PoseNode>());

  useEffect(() => {
    const tempImage = new Image();

    tempImage.onload = function (e) {
      setImageHeight(tempImage.naturalHeight);
      setImageWidth(tempImage.naturalWidth);
    };

    if (imageUrl !== null && imageUrl !== undefined) tempImage.src = imageUrl;

    return () => {};
  }, [imageUrl]);

  return (
    <div className="pose-wrapper">
      <svg
        width={imageWidth * scale}
        height={imageHeight * scale}
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        xmlns="http://www.w3.org/2000/svg"
      >
        <image href={imageUrl}></image>
        <image href={maskUrl} style={{opacity: 0.25}}></image>
        <g>
          {pose.edges.map(({ from, to }) => (
            <>
              <Line
                key={`${from}-${to}-border`}
                x1={mapX(nodeMap.get(from)!.position.x)}
                y1={mapY(nodeMap.get(from)!.position.y)}
                x2={mapX(nodeMap.get(to)!.position.x)}
                y2={mapY(nodeMap.get(to)!.position.y)}
                stroke={
                  isMoving &&
                  hoveredJoint &&
                  [from, to].indexOf(hoveredJoint) >= 0
                    ? "black"
                    : "white"
                }
                strokeWidth="3"
              />
              <Line
                key={`${from}-${to}`}
                x1={mapX(nodeMap.get(from)!.position.x)}
                y1={mapY(nodeMap.get(from)!.position.y)}
                x2={mapX(nodeMap.get(to)!.position.x)}
                y2={mapY(nodeMap.get(to)!.position.y)}
                stroke={
                  isMoving &&
                  hoveredJoint &&
                  [from, to].indexOf(hoveredJoint) >= 0
                    ? "red"
                    : "black"
                }
                strokeWidth="1"
              />
            </>
          ))}
          {pose.nodes.map((node) => (
            <Circle
              key={node.id}
              cx={mapX(node.position.x)}
              cy={mapY(node.position.y)}
              strokeWidth="2"
              stroke="white"
              r="4"
              imgWidth={imageWidth * scale}
              imgHeight={imageHeight * scale}
              onPositionUpdate={(pos) => {
                const newPos = { x: unmapX(pos.x), y: unmapY(pos.y) };

                nodeMap.set(node.id, {
                  ...node,
                  position: newPos,
                });

                setPose({
                  ...pose,
                  nodes: Array.from(nodeMap.values()),
                });
                setIsMoving(pos.active);
              }}
              onHover={(enter) => {
                setHoveredJoint(enter ? node.label : undefined);
              }}
            />
          ))}
        </g>
      </svg>
      {hoveredJoint ? (
        <div className="tooltip-pose">
          {hoveredJoint?.replace("l_", "left ")?.replace("r_", "right ")?.replace("_", " ")}
        </div>
      ) : null}
    </div>
  );
};

export default PoseEditor;

/**
 *   {debug && (
        <div className="debug">
          <strong>DEBUG:</strong>
          {pose.nodes.map((node) => (
            <div key={node.id}>
              <span style={{ display: "inline-block", width: 100 }}>
                {node.label}:
              </span>{" "}
              {node.position.x}, {node.position.y}
            </div>
          ))}
        </div>
      )}
 */
