import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import CanvasUpload from "./CanvasUpload";
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
      case 2:
        return <CanvasBoundingBox />;
      case 3:
        return <CanvasMask />;
      case 4:
        return <CanvasPose />;
      case 5:
        return <CanvasAnimation />;
      default:
        return [];
    }
  };

  return (
    <>
      {renderStep()}
    </>
  );
};

export default Canvas;
