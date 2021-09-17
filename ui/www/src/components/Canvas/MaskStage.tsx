import React, { useEffect, useRef } from "react";
import { Stage, Layer, Line, Image } from "react-konva";
import useImage from "use-image";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";

interface imgProps {
  editMode: boolean;
  urlImg: string | any;
  height: number;
  width: number
}

const MaskImage = ({ editMode, urlImg, height, width }: imgProps) => {
  const [image] = useImage(urlImg, "anonymous");
  return (
    <Image
      image={image}
      width={(height - 20) / 1.5 || 0}
      height={height - 20 || 0}
      x={width / 2 - (height - 20) / 1.5 / 2 || 0}
      y={0}
      opacity={editMode ? 0.5 : 1}
    />
  );
};

const DrawingImage = ({ editMode, urlImg, height, width }: imgProps) => {
  const [image] = useImage(urlImg, "anonymous");
  return (
    <Image
      image={image}
      width={(height - 20) / 1.5 || 0}
      height={height - 20 || 0}
      x={width / 2 - (height - 20) / 1.5 / 2 || 0}
      y={0}
      visible={editMode}
    />
  );
};

const MaskStage = ({ canvasWidth, canvasHeight }: any) => {
  const layerRef = useRef<any>(null);
  const isDrawing = useRef(false);
  const { imageUrlPose, imageUrlMask } = useDrawingStore();
  const { tool, penSize, lines, setLines, setMaskBase64 } = useMaskingStore();

  useEffect(() => {
    const uri = layerRef.current.toDataURL({ pixelRatio: 2 });
    setMaskBase64(uri)
    return () => {}
  }, [lines, setMaskBase64])

  const handleMouseDown = (e: any) => {
    isDrawing.current = true;
    const pos = e.target.getStage().getPointerPosition();
    setLines([...lines, { tool, penSize, points: [pos.x, pos.y] }]);
  };

  const handleMouseMove = (e: any) => {
    if (!isDrawing.current) {
      return;
    }
    const stage = e.target.getStage();
    const point = stage.getPointerPosition();
    let lastLine = lines[lines.length - 1];
    lastLine.points = lastLine.points.concat([point.x, point.y]);
    lines.splice(lines.length - 1, 1, lastLine);
    setLines(lines.concat());
  };

  const handleMouseUp = () => {
    isDrawing.current = false;
  };

  return (
    <div>
      <Stage
        width={canvasWidth}
        height={canvasHeight}
        onMouseDown={handleMouseDown}
        onTouchStart={handleMouseDown}
        onMousemove={handleMouseMove}
        onTouchMove={handleMouseMove}
        onMouseup={handleMouseUp}
        onTouchEnd={handleMouseUp}
      >
        <Layer>
          <DrawingImage
            editMode={true}
            urlImg={imageUrlPose}
            height={canvasHeight}
            width={canvasWidth}
          />
        </Layer>

        <Layer ref={layerRef}>
          <MaskImage
            editMode={true}
            urlImg={imageUrlMask}
            height={canvasHeight}
            width={canvasWidth}
          />
          {lines.map((line: any, i: number) => (
            <Line
              key={i}
              points={line.points}
              //stroke={editMode ? "grey" : "black"}
              stroke={"grey"}
              strokeWidth={line.penSize}
              tension={0.5}
              lineCap="round"
              //opacity={editMode ? 0.8 : 1}
              globalCompositeOperation={
                line.tool === "eraser" ? "destination-out" : "source-over"
              }
            />
          ))}
        </Layer>
      </Stage>
    </div>
  );
};

export default MaskStage;
