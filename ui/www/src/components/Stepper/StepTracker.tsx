import React, { useEffect, useState } from "react";

interface Props {
  steps: any;
  currentStepNumber: number;
  stepColor: string;
}

const Stepper = ({ steps, currentStepNumber, stepColor }: Props) => {
  const [stepsState, setSteps] = useState<any>([]);

  useEffect(() => {
    const stepsState1 = steps.map((step: any, index: number) => ({
      description: step,
      highlighted: index === 0 ? true : false,
      selected: index === 0 ? true : false,
      completed: false,
    }));
    const currentSteps = updateStep(currentStepNumber, stepsState1);
    setSteps(currentSteps);

    return () => {};
  }, [steps, currentStepNumber]);

  const updateStep = (stepNumber: number, steps: Array<{}>) => {
    const newSteps = [...steps];
    let stepCounter = 0;

    // Completed - to add a check mark
    // Selected - to fill step with color
    // Highlighted - to make text of selected step bold

    while (stepCounter < newSteps.length) {
      // Current step
      if (stepCounter === stepNumber) {
        newSteps[stepCounter] = {
          ...newSteps[stepCounter],
          highlighted: true,
          selected: true,
          completed: false,
        };
        stepCounter++;
      }
      // Past step
      else if (stepCounter < stepNumber) {
        newSteps[stepCounter] = {
          ...newSteps[stepCounter],
          highlighted: false,
          selected: true,
          completed: true,
        };
        stepCounter++;
      }
      // Future step
      else {
        newSteps[stepCounter] = {
          ...newSteps[stepCounter],
          highlighted: false,
          selected: false,
          completed: false,
        };
        stepCounter++;
      }
    }

    return newSteps;
  };

  const stepsJSX = stepsState.map((step: any, index: number) => {
    return (
      <div className="step-wrapper" key={index}>
        <div
          className="step-progress-block"
          style={{ background: `${step.selected ? stepColor : "white"}` }}
        ></div>
      </div>
    );
  });

  return <div className="stepper-wrapper-horizontal">{stepsJSX}</div>;
};

export default Stepper;
