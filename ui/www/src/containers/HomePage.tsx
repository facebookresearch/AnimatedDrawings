import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";

const HomePage = () => {
  return (
    <>
      <div className="main-content">
        <div className="home-page">
          <Container className="align-content-center">
            <Row className="align-items-center justify-content-center">
              <Col lg={4} md={6} sm={6} className="mx-2">
                <div className="mb-4">
                  <h1 className="reg-title text-primary">
                    Animate children's drawings
                  </h1>
                  <h3>
                    Bring children's drawings to life, by animating characters
                    to move around!
                  </h3>
                </div>
                <Button size="lg" className="px-4 mb-4">
                  Get Started
                </Button>
              </Col>
              <Col lg={4} md={6} sm={6} className="mx-2"></Col>
            </Row>
          </Container>
          <div className="home-img-wrapper">
            <img alt="example 5" src="/assets/HomePageImg.svg" />
          </div>
          <div className="home-footer text-center" onClick={() => window.location.replace("/home/#fair")}>
            <h4>Presented by Facebook AI Research</h4>
            <i className="bi bi-arrow-down-short"/>
          </div>
        </div>
      </div>
      <div className="main-content" id="fair"></div>
    </>
  );
};

export default HomePage;
