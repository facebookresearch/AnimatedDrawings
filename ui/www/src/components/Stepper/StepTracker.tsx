import React, { useEffect, useState } from "react";
import classnames from "classnames";

interface Props {
  steps: any;
  currentStepNumber: number;
}

type stepInfo = {
  description: string;
  highlighted: boolean;
  selected: boolean;
  completed: boolean;
};

const StepTracker = ({ steps, currentStepNumber }: Props) => {
  const [stepsState, setSteps] = useState<stepInfo[]>([]);

  useEffect(() => {
    const stepsState1: stepInfo[] = steps.map((step: any, index: number) => ({
      description: step,
      highlighted: index === 0 ? true : false,
      selected: index === 0 ? true : false,
      completed: false,
    }));
    const currentSteps: stepInfo[] = updateStep(currentStepNumber, stepsState1);
    setSteps(currentSteps);

    return () => {};
  }, [steps, currentStepNumber]);

  const updateStep = (stepNumber: number, steps: stepInfo[]) => {
    const newSteps = [...steps];
    let stepCounter = 0;

    // Completed - to fill step with lighht blue
    // Selected - to fill step with color of selected
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
          className={classnames(
            "step-progress-block",
            { "step-completed": step.completed },
            { "step-progress-block-current": step.highlighted }
          )}
        ></div>
      </div>
    );
  });

  return <div className="stepper-wrapper-horizontal">{stepsJSX}</div>;
};

export default StepTracker;
