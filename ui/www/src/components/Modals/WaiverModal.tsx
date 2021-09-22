import React from "react";
import { createPortal } from "react-dom";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import Step2 from "../Stepper/Step2";

interface modalProps {
  showModal: boolean;
  setShowModal: (show: boolean) => void;
}

const WaiverModal = ({ showModal, setShowModal }: modalProps) => {
  const { agreeTerms, setCurrentStep } = useStepperStore();
  const { uuid } = useDrawingStore();
  const { isLoading, setConsentAnswer } = useDrawingApi((err) => {});

  const handleNext = async () => {
    let response = agreeTerms ? 1 : 0;
    console.log(response)
    setShowModal(!showModal);
    setCurrentStep(3);
    // After backend is running uncomment this out.
    /*try {
      await setConsentAnswer(uuid, response, () => {
        setShowModal(!showModal);
        setCurrentStep(3);
      });
    } catch (error) {
      console.log(error);
    }*/
  };

  return showModal
    ? createPortal(
        <div className="waiver-step-container-wrap">
          <div className="main-content">
            <div className="navbar-title-waiver">
              <h3>ANIMATED DRAWINGS</h3>
            </div>
            <div className="share-page">
              <Step2
                showModal={showModal}
                //isLoading={isLoading}
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
