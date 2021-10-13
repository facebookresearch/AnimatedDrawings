import React from "react";
import { useHistory } from "react-router-dom";
import { Container, Row, Col, Button } from "react-bootstrap";

const HomePage = () => {
  const history = useHistory();
  return (
    <div className="main-content bg-home" id="home">
      <div className="home-page">
        <Container className="align-content-center home-info">
          <Row className="justify-content-center">
            <Col lg={6} md={6} sm={6} className="text-center mb-4">
              <h2 className="mb-3">
                ANIMATED <span className="text-info">DRAWINGS</span>
              </h2>
            </Col>
          </Row>
          <Row className="justify-content-center">
            <Col lg={5} md={6} sm={6} className="text-center mb-4">
              <h3>
                Bring children's drawings to life, by animating characters to
                move around!
              </h3>
            </Col>
          </Row>
          <Row className="justify-content-center">
            <Col lg={6} md={10} xs={12} className="mb-4 justify-content-center">
              <div className="gif-wrapper">
                <div className="gif-div"></div>
                <div className="gif-shadow-div"></div>
              </div>
            </Col>
          </Row>
          <Row className="justify-content-center">
            <Col lg={3} md={4} className="text-center">
              <Button
                block
                size="lg"
                className="px-4 py-2"
                onClick={() => history.push("/canvas")}
              >
                Get Started
              </Button>
            </Col>
          </Row>
        </Container>
        <div className="home-footer-credits py-2">
          <h4>
            <span className="rg-1">Presented By</span> FACEBOOK AI{" "}
            <span className="rg-1">Research</span>
          </h4>
        </div>
        <div
          className="home-footer text-center py-2"
          onClick={() => history.push("/about")}
        >
          <h4>ABOUT THIS DEMO</h4>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
