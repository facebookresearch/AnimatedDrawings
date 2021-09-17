import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import CanvasUpload from "./CanvasUpload";
import CanvasDetecting from "./CanvasDetecting";
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
        return <CanvasUpload />;
      case 3:
        return <CanvasDetecting />;
      case 4:
        return <CanvasMask />;
      case 5:
        return <CanvasPose />;
      case 6:
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
