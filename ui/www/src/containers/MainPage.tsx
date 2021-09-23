import React from "react";
import { Container, Row, Col } from "react-bootstrap";
import Navbar from "../components/Navbars/Navbar";
import Canvas from "../components/Canvas/Canvas";
import StepsContainer from "../components/Stepper/StepsContainer";
import useDrawingStore from "../hooks/useDrawingStore";

const MainPage = () => {
  const { uuid } = useDrawingStore();
  return (
    <div className="main-content bg-main">
      <Navbar />
      <a
        href={`mailto:animatingdrawingsfb@gmail.com?subject=Questions%20or%20Feedback&body=Please%20include%20the%20following%20ID%20in%20your%20message.%0AUUID:%20${
          uuid !== "" ? uuid : "Preload_Step"
        }`}
        target="_blank"
        rel="noreferrer"
      >
        <div className="feedback-wrapper">
          <i className="bi bi-info-square-fill" />
        </div>
      </a>
      <div className="main-page">
        <Container>
          <Row className="align-items-center py-2 px-lg-2">
            <Col lg={6} md={6} sm={12} className="ml-auto mb-2 order-sm-2">
              <Canvas />
            </Col>
            <Col
              lg={4}
              md={4}
              sm={12}
              className="mt-sm-6 align-self-start px-2 order-sm-1"
            >
              <StepsContainer />
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default MainPage;
