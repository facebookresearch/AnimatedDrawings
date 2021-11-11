import React, { useState } from "react";
import { Container, Row, Col } from "react-bootstrap";
import Canvas from "../components/Canvas/Canvas";
import StepsContainer from "../components/Stepper/StepsContainer";
import useDrawingStore from "../hooks/useDrawingStore";
import useStepperStore from "../hooks/useStepperStore";
import AboutModal from "../components/Modals/AboutModal";

const MainPage = () => {
  const { uuid } = useDrawingStore();
  const { currentStep } = useStepperStore();
  const [showModal, setShowModal] = useState(false);
  return (
    <div className="main-content bg-main">
      <div className="navbar-title">
        <a href="/">
          <h2 className="mb-3">
            ANIMATED <span className="text-info">DRAWINGS</span>
          </h2>
        </a>
      </div>
      <a
        href={`https://docs.google.com/forms/d/e/1FAIpQLSfynXUEVc0YvSYGXN3BCFjl7uNthyEkxqibsNHn3pqA_Wt8Hg/viewform?entry.1387562397=${
          uuid !== "" ? uuid : "Preload Step [No ID]"
        }`}
        target="_blank"
        rel="noreferrer"
      >
        <div className="feedback-wrapper">
          <h4 className="d-none d-lg-block">
            Feedback <i className="bi bi-info-square-fill ml-2 h2"></i>
          </h4>
          <i className="bi bi-info-square-fill h2 d-inline-block d-block d-sm-none" />
        </div>
      </a>
      <div className="main-page">
        <Container>
          <Row className="align-items-center py-2 px-lg-2">
            <Col
              lg={6}
              md={12}
              xs={12}
              className="mb-2 order-sm-2 justify-content-center"
            >
              <Canvas />
            </Col>
            <Col
              lg={5}
              md={8}
              sm={10}
              xs={12}
              className="col-left ml-auto mr-auto mt-sm-6 align-self-start px-3 order-sm-1 pt-md-4"
            >
              <StepsContainer />
            </Col>
          </Row>
        </Container>
        {currentStep === 5 && (
          <>
            <div className="home-footer-credits py-2">
              <h4> PRESENTED BY FACEBOOK AI RESEARCH</h4>
            </div>
            <div
              className="home-footer d-none d-lg-block text-center py-2"
              onClick={() => setShowModal(true)}
            >
              <h3>ABOUT THIS DEMO</h3>
            </div>
          </>
        )}
      </div>
      <AboutModal showModal={showModal} setShowModal={setShowModal} />
    </div>
  );
};

export default MainPage;
