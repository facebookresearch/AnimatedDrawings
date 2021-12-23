import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";
import useLogPageView from "../hooks/useLogPageView";

const SharingPage = () => {
  useLogPageView("Error", "");
  return (
    <div className="main-content bg-main">
      <div className="navbar-title-waiver">
        <h2>
          ANIMATED <span className="text-info">DRAWINGS</span>
        </h2>
      </div>
      <div className="share-page">
        <Container fluid="md" className="mt-3 align-content-center">
          <Row className="align-items-center justify-content-center py-2 mt-1 px-lg-2">
            <Col lg={8} md={12} sm={12} className="mb-2 mx-2 pl-lg-0">
              <div className="canvas-wrapper">
                <div className="canvas-background">
                  <div className="error-message-div">
                    <h2>Oh no, something went wrong!</h2>
                    <br />
                    <p>
                      A lot of people are trying to animate their drawings right
                      now, and our servers are struggling to keep up!
                    </p>
                    <br />
                    <p>Please try again in a few minutes.</p>
                  </div>
                </div>
                <Row className="justify-content-center mt-3">
                  <Col lg={6} md={6} xs={12}>
                    <Button
                      block
                      size="lg"
                      variant="primary"
                      className="py-lg-3 mt-lg-3 my-1"
                      href="/"
                    >
                      Go to homepage
                    </Button>
                  </Col>
                  <Col lg={6} md={6} xs={12} className="text-center">
                    <Button
                      block
                      size="lg"
                      variant="info"
                      className="py-lg-3 mt-lg-3 my-1 text-primary"
                      href="https://sketch.metademolab.com/share/cf1671e5e6f04254b5bb6b12ad4f7ace/wave_hello_3"
                    >
                      See example animation
                    </Button>
                  </Col>
                </Row>
              </div>
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default SharingPage;
