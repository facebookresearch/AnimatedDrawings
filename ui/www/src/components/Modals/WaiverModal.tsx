import React, { Fragment } from "react";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import Step2 from "../Stepper/Step2";

interface modalProps {
  showModal: boolean;
  setShowModal: (show: boolean) => void;
}

const WaiverModal = ({ showModal, setShowModal }: modalProps) => {
  const { setAgreeTerms, setCurrentStep } = useStepperStore();
  const { uuid } = useDrawingStore();
  const { isLoading, setConsentAnswer } = useDrawingApi((err) => {});

  const handleNext = async (res: boolean) => {
    let response = res ? 1 : 0;
    try {
      setAgreeTerms(res)
      await setConsentAnswer(uuid, response, () => {
        setShowModal(false);
        console.log(response)
      });
      setCurrentStep(2);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <Fragment>
      {showModal ? (
        <div className="waiver-step-container-wrap">
          <div className="main-content bg-waiver">
            <div className="navbar-title-waiver">
              <h2>ANIMATED <span className="text-info">DRAWINGS</span></h2>
            </div>
            <div className="share-page">
              <Step2
                showModal={showModal}
                isLoading={isLoading}
                setShowModal={setShowModal}
                handleNext={handleNext}
              />
            </div>
          </div>
        </div>
      ) : null}
    </Fragment>
  );
};

export default WaiverModal;
