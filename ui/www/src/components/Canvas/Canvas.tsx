import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import CanvasUpload from "./CanvasUpload";
import CanvasDetecting from "./CanvasDetecting";
import CanvasBoundingBox from "./CanvasBoundingBox";
import CanvasMask from "./CanvasMask";
import CanvasPose from "./CanvasPose";
import CanvasAnimation from "./CanvasAnimation";

const Canvas = () => {
  const { currentStep, } = useStepperStore();

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <CanvasUpload />;
      case 3:
        return <CanvasDetecting />;
      case 4:
        return <CanvasBoundingBox />;
      case 5:
        return <CanvasMask />;
      case 6:
        return <CanvasPose />;
      case 7:
        return <CanvasAnimation />;
      default:
        return [];
    }
  };

  return (
    <div>
      {renderStep()}
    </div>
  );
};

export default Canvas;
