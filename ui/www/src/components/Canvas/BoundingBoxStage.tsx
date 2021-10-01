import React, { useEffect, useRef, Fragment } from "react";
import { Stage, Layer, Image, Rect, Transformer } from "react-konva";
import useImage from "use-image";
import useDrawingStore from "../../hooks/useDrawingStore";
import { BoundingBox } from "./CanvasBoundingBox";

interface imgProps {
  urlImg: string | any;
  height: number;
  width: number;
  canvasWidth: number;
  canvasHeight: number;
  onMouseDown?: () => void;
}

interface BBProps {
  shapeProps: BoundingBox;
  isSelected: boolean;
  canvasWidth: number;
  canvasHeight: number;
  onSelect?: () => void;
  onChange: (atrr: object) => void;
}

const DrawingImage = ({ urlImg, height, width, canvasWidth, canvasHeight }: imgProps) => {
  const [image] = useImage(urlImg, "anonymous");
  return (
    <Image 
      image={image} 
      width={width || 0}
      height={height || 0} 
      x={canvasWidth/2 - width/2 || 0} 
      //x={0} 
      y={canvasHeight/2 - height/2 ||0} 
      //y={0} 
    />
  );
};

const Annotation = ({
  shapeProps,
  isSelected,
  canvasWidth,
  canvasHeight,
  onSelect,
  onChange,
}: BBProps) => {
  const shapeRef = useRef<HTMLCanvasElement | any>(null);
  const transformRef = useRef<HTMLCanvasElement | any>(null);

  useEffect(() => {
    if (isSelected) {
      // we need to attach transformer manually
      transformRef.current.nodes([shapeRef.current]);
      transformRef.current.getLayer().batchDraw();
    }
  }, [isSelected]);

  const onMouseEnter = (event: MouseEvent | any) => {
    event.target.getStage().container().style.cursor = "move";
  };

  const onMouseLeave = (event: MouseEvent | any) => {
    event.target.getStage().container().style.cursor = "crosshair";
  };

  const limitBoundingBox = (pos: { x: number; y: number }) => {
    const node = shapeRef.current;
    const newRect = node.getClientRect();
    let newPos = { ...pos };
    if (pos.x < 0) {
      newPos.x = 0;
    }
    if (pos.y < 0) {
      newPos.y = 0;
    }
    if (pos.x + newRect.width > canvasWidth) {
      newPos.x = canvasWidth - newRect.width;
    }
    if (pos.y + newRect.height > canvasHeight) {
      newPos.y = canvasHeight - newRect.height;
    }
    return newPos;
  };

  return (
    <Fragment>
      <Rect
        fill="transparent"
        stroke="#00BCAD"
        onMouseDown={onSelect}
        onTap={onSelect}
        ref={shapeRef}
        {...shapeProps}
        draggable
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        onDragEnd={(event) => {
          onChange({
            ...shapeProps,
            x: event.target.x(),
            y: event.target.y(),
          });
        }}
        onTransformEnd={(event) => {
          // transformer is changing scale of the node
          // and NOT its width or height
          // but in the store we have only width and height
          // to match the data better we will reset scale on transform end
          const node = shapeRef.current;
          const scaleX = node.scaleX();
          const scaleY = node.scaleY();

          // we will reset it back
          node.scaleX(1);
          node.scaleY(1);
          onChange({
            ...shapeProps,
            x: node.x(),
            y: node.y(),
            width: Math.max(5, node.width() * scaleX),
            height: Math.max(node.height() * scaleY),
          });
        }}
        dragBoundFunc={(pos) => limitBoundingBox(pos)}
      />

      <Transformer
        ref={transformRef}
        rotateEnabled={false}
        boundBoxFunc={(oldBox, newBox) => {
          // limit resize
          if (newBox.width < 5 || newBox.height < 5) {
            return oldBox;
          }
          return newBox;
        }}
      />
    </Fragment>
  );
};

const BoundingBoxStage = ({ canvasWidth, canvasHeight,imageWidth, imageHeight  }: any) => {
  const { drawing, boundingBox, setBox } = useDrawingStore();

  const handleMouseEnter = (event: MouseEvent | any) => {
    event.target.getStage().container().style.cursor = "crosshair";
  };

  const checkDeselect = (e: TouchEvent | any) => {
    const clickedOnEmpty = e.target === e.target.getStage();
    if (clickedOnEmpty) {
      return
    }
  };

  return (
    <div>
      <Stage
        width={canvasWidth}
        height={canvasHeight || 0}
        onMouseEnter={handleMouseEnter}
        onTouchStart={checkDeselect}
      >
        <Layer>
          <DrawingImage
            urlImg={drawing}
            width={imageWidth} //Original dimensions to fit in the square
            height={imageHeight}
            canvasWidth={canvasWidth}
            canvasHeight={canvasHeight}
          />
          <Annotation
            shapeProps={boundingBox}
            isSelected={true}
            canvasWidth={canvasWidth}
            canvasHeight={canvasHeight}
            onChange={(newAttrs: any) => {
              setBox(newAttrs);
            }}
          />
        </Layer>
      </Stage>
    </div>
  );
};

export default BoundingBoxStage;
