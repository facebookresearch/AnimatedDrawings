import React from "react";
import { useHistory } from "react-router-dom";
import { Container, Row, Col } from "react-bootstrap";

const AboutPage = () => {
  const history = useHistory();
  return (
    <div className="main-content bg-about" id="about">
      <div className="home-page">
        <Container className="align-content-center">
          <Row className="justify-content-center">
            <Col lg={6} md={10} xs={12}>
              <h2 className="mb-3 text-center">ABOUT THIS DEMO</h2>
              <p>
                Children’s drawings have a wonderful inventiveness, energy, and
                variety. We focus on the consequence of all that variety in
                their drawings of humans as we develop an algorithm to bring
                them to life through automatic animation.
              </p>
              <br />
              <p>
                {" "}
                Our goal in this work is to develop a pipeline that can with
                high probability, and without either adult or child
                intervention, identify the humans-like figures in a drawing,
                segment them from the background, rig them by locating the key
                bones, body parts, and joints, and animate them using motion
                capture data. We assess the quality of our results by comparing
                them with crowd-sourced manual annotations and through a series
                of perceptual user studies.
              </p>
              <br />
              <p>
                Built by Jesse Smith, Jessica Hodgins, Somya Jain, Sahir Gomez,
                Somayan Chakrabarti, Clarence Edmondson III, and friends at
                Facebook AI Research.
              </p>
            </Col>
          </Row>
        </Container>
      </div>
      <div className="wr-about-1" onClick={() => history.push("/")}>
        <i className="bi bi-x-lg h1"/>
      </div>
    </div>
  );
};

export default AboutPage;
