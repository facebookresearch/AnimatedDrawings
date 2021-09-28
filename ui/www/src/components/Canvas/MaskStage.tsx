import React, { useRef } from "react";
import { Stage, Layer, Line, Image } from "react-konva";
import useImage from "use-image";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";

interface imgProps {
  urlImg: string | any;
  height: number;
  width: number;
}

const MaskImage = ({ urlImg, height, width }: imgProps) => {
  const [image] = useImage(urlImg, "anonymous");
  return (
    <Image
      image={image}
      width={width || 0}
      height={height || 0}
      x={0}
      y={0}
      opacity={1}
    />
  );
};

const DrawingImage = ({ urlImg, height, width }: imgProps) => {
  const [image] = useImage(urlImg, "anonymous");
  return (
    <Image
      image={image}
      width={width || 0}
      height={height || 0}
      x={0}
      y={0}
      opacity={0.5}
    />
  );
};

/**
 * Use forwardRef to send the layer ref to the parent component.
 * this is the mask sent to the server.
 */
const MaskStage = React.forwardRef(
  ({ scale, canvasWidth, canvasHeight }: any, ref: any) => {
    const isDrawing = useRef(false);
    const { imageUrlPose, imageUrlMask } = useDrawingStore();
    const {
      tool,
      penSize,
      lines,
      setLines,
    } = useMaskingStore();

    const handleMouseDown = (e: { target: Event | any }) => {
      isDrawing.current = true;
      //const pos = e.target.getStage().getPointerPosition();
      const pos = e.target.getStage().getRelativePointerPosition()

      setLines([...lines, { tool, penSize, points: [pos.x, pos.y] }]);
    };

    const handleMouseMove = (e: { target: Event | any }) => {
      if (!isDrawing.current) {
        return;
      }
      const stage = e.target.getStage();
      //const point = stage.getPointerPosition();
      const point = stage.getRelativePointerPosition()
      let lastLine = lines[lines.length - 1];
        lastLine.points = lastLine.points.concat([point.x, point.y]);
        lines.splice(lines.length - 1, 1, lastLine);
        setLines(lines.concat());
    };

    const handleMouseUp = () => {
      isDrawing.current = false;
    };

    return (
      <Stage
        width={canvasWidth * scale}
        height={canvasHeight * scale}
        onMouseDown={handleMouseDown}
        onTouchStart={handleMouseDown}
        onMousemove={handleMouseMove}
        onTouchMove={handleMouseMove}
        onMouseup={handleMouseUp}
        onTouchEnd={handleMouseUp}
        scale={{ x: scale, y: scale }}
      >
        <Layer ref={ref}>
          <MaskImage
            urlImg={imageUrlMask}
            height={canvasHeight}
            width={canvasWidth}
          />
          {lines.map((line: any, i: number) => (
            <Line
              key={i}
              points={line.points}
              stroke={line.tool === "eraser" ? "dark" : "white"}
              strokeWidth={line.penSize}
              tension={0.5}
              lineCap="round"
            />
          ))}
        </Layer>
        <Layer>
          <DrawingImage
            urlImg={imageUrlPose}
            height={canvasHeight}
            width={canvasWidth}
          />
        </Layer>
      </Stage>
    );
  }
);

export default MaskStage;
