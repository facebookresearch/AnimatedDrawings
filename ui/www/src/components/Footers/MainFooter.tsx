import React from "react";
import { Row, Col } from "react-bootstrap";

interface props {
  uuid?: string;
  showAll?: boolean;
  setShowModal: (res: boolean) => void;
}

export default function MainFooter({ uuid, showAll, setShowModal }: props) {
  return (
    <div className="main-page-footer">
      <Row className="mb-3">
        {showAll ? (
          <Col
            lg="4"
            xs="7"
            className="feedback-wrapper text-center px-0 order-lg-2"
            onClick={() => setShowModal(true)}
          >
            ABOUT THIS DEMO
          </Col>
        ) : (
          <Col lg="4" xs="7"></Col>
        )}
        <Col
          lg="4"
          xs="5"
          className="feedback-wrapper text-right pr-lg-4 order-lg-3"
        >
          <a
            href={`https://docs.google.com/forms/d/e/1FAIpQLSfynXUEVc0YvSYGXN3BCFjl7uNthyEkxqibsNHn3pqA_Wt8Hg/viewform?entry.1387562397=${
              uuid !== "" ? uuid : "Preload Step [No ID]"
            }`}
            target="_blank"
            rel="noreferrer"
            className="text-primary"
          >
            FEEDBACK
            <i className="bi bi-info-circle-fill ml-2 h3"></i>
          </a>
        </Col>
        {showAll ? (
          <Col lg="4" xs="12" className="order-lg-1 text-center pl-0">
            PRESENTED BY FACEBOOK AI RESEARCH
          </Col>
        ) : (
          <Col lg="4" xs="12"></Col>
        )}
      </Row>
    </div>
  );
}

