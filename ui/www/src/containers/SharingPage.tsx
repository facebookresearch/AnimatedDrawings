import React, { useState } from "react";
import { useParams, useHistory } from "react-router-dom";
import { Container, Row, Col, Badge } from "react-bootstrap";
import CanvasShare from "../components/Canvas/CanvasShare";

const SharingPage = () => {
  const { uuid, type } = useParams<{ uuid: string; type: string }>();
  const history = useHistory();
  const [reported, setReported] = useState(false);

  return (
    <>
      <div className="main-content bg-share">
        <div className="navbar-title-waiver">
          <h2>
            ANIMATED <span className="text-info">DRAWINGS</span>
          </h2>
        </div>
        <div className="share-page">
          <Container fluid="md" className="mt-3 align-content-center">
            <Row className="align-items-center justify-content-center py-2 mt-1 px-lg-2">
              <Col lg={12} md={12} sm={12} className="mb-2 mx-2 pl-lg-0">
                <CanvasShare uuid={uuid} animationType={type} />
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
          {!reported ? (
            <div
              className="footer-report-content py-2"
              onClick={() => setReported(true)}
            >
              <h4>Report something wrong</h4>
            </div>
          ) : (
            <div
              className="footer-report-content py-2"
              //onClick={() => history.push("/about")}
            >
              <h2>
                <Badge variant="success">Reported</Badge>
              </h2>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default SharingPage;
