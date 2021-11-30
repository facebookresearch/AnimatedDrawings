import React, { Fragment, useState } from "react";
import classnames from "classnames";
import SegmentationHelpModal from "../Modals/SegmentationHelpModal";

interface TitleProps {
  currentStep: number;
}

const titles = [
  {
    step: 1,
    firstLine: "Upload a",
    secondLine: "drawing",
  },
  {
    step: 2,
    firstLine: "Finding the",
    secondLine: "human-like ",
    thirdLine: "character",
  },
  {
    step: 3,
    firstLine: "Separating",
    secondLine: "character",
    showHelp: true,
  },
  {
    step: 4,
    firstLine: "Finding",
    secondLine: "character joints",
  },
  {
    step: 5,
    firstLine: "Add",
    secondLine: "animation",
  },
];

const StepTitle = ({ currentStep }: TitleProps) => {
  const [showModal, setModal] = useState(false);
  const title = titles.find((i) => i.step === currentStep);

  return (
    <Fragment>
      <h1
        className={classnames("step-title", {
          "ml-2": currentStep === 5,
        })}
      >
        {title?.firstLine}{" "}
        <span className="text-info">{title?.secondLine}</span>
        {title?.thirdLine}{" "}
        {title?.showHelp && (
          <i
            onClick={() => {
              setModal(true);
            }}
            className="bi bi-info-circle-fill ml-2 h2"
            style={{ cursor: "pointer" }}
          />
        )}
      </h1>
      <SegmentationHelpModal
        showModal={showModal}
        handleModal={() => setModal(!showModal)}
        title={"HOW TO FIX"}
      />
    </Fragment>
  );
};

export default StepTitle;
