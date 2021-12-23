import React, { useState } from "react";
import { Container, Row, Col } from "react-bootstrap";
import Canvas from "../components/Canvas/Canvas";
import StepsContainer from "../components/Stepper/StepsContainer";
import useDrawingStore from "../hooks/useDrawingStore";
import useStepperStore from "../hooks/useStepperStore";
import AboutModal from "../components/Modals/AboutModal";
import HomeFooter from "../components/Footers/HomeFooter";
import ErrorPage from "./ErrorPage";

const MainPage = () => {
  const { uuid } = useDrawingStore();
  const { errorCode } = useStepperStore();
  const [showModal, setShowModal] = useState(false);

  if (errorCode !== 0) {
    return <ErrorPage />;
  }

  return (
    <div className="main-content bg-main">
      <div className="navbar-title">
        <a href="/">
          <h2 className="mb-3">
            ANIMATED <span className="text-info">DRAWINGS</span>
          </h2>
        </a>
      </div>
      <div className="main-page">
        <Container>
          <Row className="align-items-center justify-content-center py-2 px-lg-2">
            <Col
              lg={6}
              md={12}
              sm={12}
              xs={12}
              className="order-lg-2 mb-2 justify-content-center"
            >
              <Canvas />
            </Col>
            <Col
              lg={6}
              md={12}
              sm={12}
              xs={12}
              className="order-lg-1 ml-auto mr-auto align-self-start px-3"
            >
              <StepsContainer />
            </Col>
          </Row>
        </Container>
      </div>
      <HomeFooter uuid={uuid} setShowModal={setShowModal} />
      <AboutModal showModal={showModal} setShowModal={setShowModal} />
    </div>
  );
};

export default MainPage;
