import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";

interface Props {
  showModal: boolean;
  isLoading: boolean;
  setShowModal: (show: boolean) => void;
  handleNext: (res: boolean) => void
}

const WaiverStep = ({ showModal, isLoading, setShowModal, handleNext }: Props) => {

  return (
    <Container>
      <Row className="align-items-center justify-content-center">
        <Col lg={6} md={12} sm={12} className="ml-auto mr-auto">
          <Row>
            <Col></Col>
            <Col className="text-right">
              <Button
                size="sm"
                variant="link"
                className="text-dark"
                onClick={() => setShowModal(!showModal)}
              >
                Back
              </Button>
            </Col>
          </Row>
          <div className="waiver-step-container custom-scrollbar ml-auto mr-auto">
            <h2>
              Would you like to <br className="d-none d-lg-block" />
              help our research?
            </h2>
            <br />
            <p>
              Thanks for your interest in our Animated Drawings demo (“Demo”).
              It is still a work in progress and, to make it more robust, we
              need to collect additional drawings for training. In particular,
              we would like to use for research purposes the drawings that
              you’ve uploaded to the Demo (“Materials”), and any modifications
              or adjustments made by you using the tools and functionalities
              made available to you in connection with the Demo
              (“Modifications”), but first we’d like to make sure you’re okay
              with how we’ll use it for such purposes. If you aren’t, you can
              opt out of allowing us to use such Materials and Modifications for
              our research purposes by clicking “Disagree” below, and can still
              use the Demo, subject to the{" "}
              <a
                href="/terms"
                target="_blank"
                rel="noreferrer"
                className="bold"
              >
                Animated Drawings Supplemental Terms of Service
              </a>{" "}
              and{" "}
              <a
                href="https://www.facebook.com/terms.php"
                target="_blank"
                rel="noreferrer"
                className="bold"
              >
                Meta Platform, Inc.’s Terms of Service
              </a>
              . Granting permission for research uses by clicking “Agree” below
              is totally optional.
            </p>
            <p>In plain English, here is our request:</p>
            <p>
              1. Are you willing to let us use your submitted Materials and
              Modifications to help make the tool better? We will not associate
              such Materials and Modifications with your name, your child’s
              name, photo metadata or any other personally identifiable
              information. Such Materials and Modifications will be used to
              train a model to better identify, segment and place joints on
              hand-drawn characters. The deidentified Materials and
              Modifications may also be sent to human viewers to ensure quality
              annotations.
            </p>
            <p>
              2. The Materials and Modifications also may be used as part of an
              academic research paper or video and may be used in future
              initiatives to encourage additional image collection. Are you
              willing to let us publish your or your child’s Materials and
              Modifications for these research purposes? Again, no personal
              information would be included with the Materials or Modifications.
            </p>
            <p>
              3. Releasing a public dataset is a useful way to encourage
              research within that area. Are you willing to let us include your
              or your child’s Materials in a publicly available database so that
              other researchers can work on creativity tools for children?
              Again, we will not associate any personal information with the
              Materials. The only thing that will be included in the database is
              a photograph of the Materials and the annotations (e.g., the
              separation from the background, and the bone structure for the
              character).
            </p>
            <p>
              4. You grant to Meta and its affiliated companies, licensees, and
              representatives a perpetual, irrevocable, nonexclusive,
              royalty-free license to reproduce, distribute, perform and display
              (publicly or otherwise), modify, create derivative works from,
              host, and otherwise use the Materials and Modifications for the
              following purposes: (1) to improve the Demo, including training
              the model used in connection with the Demo; (2) to have
              professional annotators, crowdsourced workers, or our
              representatives annotate and clean the Materials and
              Modifications; (3) to publicly release or make available the
              Materials as part of an open source dataset; (4) as part of an
              academic research paper or video; and (5) as part of future
              initiatives to encourage additional image collection.
            </p>
            <p>
              5. For additional information, please see{" "}
              <a
                href="/about"
                target="_blank"
                rel="noreferrer"
                className="bold"
              >
                “About This Demo”
              </a>
            </p>
          </div>
          <Row className="justify-content-center px-3">
            <Col lg={6} md={4} xs={12} className="order-lg-2 text-center">
              <Button
                block
                size="lg"
                className="py-3 my-2"
                onClick={() => handleNext(true)}
              >
                Agree
              </Button>
            </Col>
            <Col lg={6} md={4} xs={12} className="order-lg-1">
              <Button
                block
                size="lg"
                variant="outline-primary"
                className="py-3 my-2"
                onClick={() => handleNext(false)}
              >
                Disagree
              </Button>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default WaiverStep;
