import React from "react";
import { createPortal } from "react-dom";
import useStepperStore from "../../hooks/useStepperStore";
import Step2 from "../Stepper/Step2";

interface modalProps {
  showModal: boolean;
  setShowModal: (show: boolean) => void;
}

const WaiverModal = ({ showModal, setShowModal }: modalProps) => {
  const { setCurrentStep } = useStepperStore();

  const handleNext = () => {
    setShowModal(!showModal);
    setCurrentStep(3);
  };

  return showModal
    ? createPortal(
        <div className="waiver-step-container2">
          <div className="main-content">
            <div className="navbar-title">
              <h3>ANIMATED DRAWINGS</h3>
            </div>
            <div className="share-page">
              <Step2
                showModal={showModal}
                setShowModal={setShowModal}
                handleNext={handleNext}
              />
            </div>
          </div>
        </div>,
        document.body
      )
    : null;
};

export default WaiverModal;
