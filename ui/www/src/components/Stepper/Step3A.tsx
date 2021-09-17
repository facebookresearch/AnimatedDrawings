import React from "react";
import { Button, Spinner } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import useMaskingStore from "../../hooks/useMaskingStore";

const Step3A = () => {
  const { uuid } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();
  const { maskBase64 } = useMaskingStore();
  const { isLoading, setMask } = useDrawingApi((err) => {
    console.log(err);
  });

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }

      if (clickType === "next" && uuid) {
        const response = await fetch(maskBase64);
        const blob = await response.blob();
        const file = new File([blob], "mask.png", {
          type: "image/png",
          lastModified: Date.now()
        })
        await setMask(uuid!, file, () => {
          console.log("ok")
          setCurrentStep(currentStep + 1);
        });
      }
      if (clickType === "previous") {
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <div className="step-actions-container">
        <h4>Step 3/4</h4>
        <h1 className="reg-title">Segmenting</h1>
        <p>
          Using the box, we’re now extracting a segmentation mask to separate
          the character from the background.
        </p>
      
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          size="sm"
          disabled={false}
          onClick={() => handleClick("previous")}
        >
          Previous
        </Button>{" "}
        <Button
          size="sm"
          className="border border-dark text-dark px-3"
          disabled={isLoading}
          onClick={() => handleClick("next")}
        >
          {isLoading ? (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
          ) : (
            "Next"
          )}
        </Button>
      </div>
    </>
  );
};

export default Step3A;
