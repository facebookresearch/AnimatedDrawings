import React, { Fragment } from "react";
import { Container, Row, Col } from "react-bootstrap";

interface modalProps {
  showModal: boolean;
  setShowModal: (show: boolean) => void;
}

const AboutModal = ({ showModal, setShowModal }: modalProps) => {
  return (
    <Fragment>
      {showModal ? (
        <div className="waiver-step-container-wrap">
          <div className="main-content bg-about">
            <div className="about-page">
              <Container className="align-content-center">
                <Row className="justify-content-center">
                  <Col lg={6} md={10} xs={12}>
                    <h2 className="mb-3 text-center">ABOUT THIS DEMO</h2>
                    <p>
                      Children’s drawings have a wonderful inventiveness,
                      energy, and variety. We focus on the consequence of all
                      that variety in their drawings of humans as we develop an
                      algorithm to bring them to life through automatic
                      animation.
                    </p>
                    <br />
                    <p> This demo builds upon <a href="https://github.com/facebookresearch/detectron2" target="_blank" rel="noreferrer" className="bold"> Detectron2</a> and 
                      <a href="https://github.com/MVIG-SJTU/AlphaPose" target="_blank" rel="noreferrer"> AlphaPose</a>. Motion capture data comes from the{" "}
                      <a href="http://mocap.cs.cmu.edu/" target="_blank" rel="noreferrer">CMU Graphics Motion Capture Lab</a> and
                      <a href="https://www.mixamo.com/" target="_blank" rel="noreferrer"> Mixamo</a>.
                    </p>
                    <br />
                    <p>
                      Built by Jesse Smith, Jessica Hodgins, Somya Jain, Sahir
                      Gomez, Somayan Chakrabarti, Clarence Edmondson III,
                      Qingyuan Zheng, and friends at Facebook AI Research.
                    </p>
                  </Col>
                </Row>
              </Container>
            </div>
            <div className="wr-about-1" onClick={() => setShowModal(false)}>
              <i className="bi bi-x-lg h1" />
            </div>
          </div>
        </div>
      ) : null}
    </Fragment>
  );
};

export default AboutModal;
