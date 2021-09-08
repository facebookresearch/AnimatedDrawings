import React from "react";
import { Container, Row, Col } from "react-bootstrap";
import Navbar from "../components/Navbar";
import Canvas from "../components/Canvas/Canvas";
import ActionsContainer from "../components/Stepper/ActionsContainer";

const MainPage = () => {
  return (
    <div className="main-content">
      <Navbar />
      <div className="main-page">
        <Container fluid="md" className="mt-3 align-content-center">
          <Row className="align-items-center justify-content-center py-2 mt-1 px-lg-2">
            <Col lg={6} md={12} sm={12} className="mb-2 mx-2 pl-lg-0">
              <Canvas />
            </Col>
            <Col lg={4} md={12} sm={12} className="mt-sm-6 align-self-start px-2">
              <ActionsContainer />
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default MainPage;
