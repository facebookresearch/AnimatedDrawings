import React, { useState, useEffect } from "react";
import { Modal, Button, Row, Col } from "react-bootstrap";
import {
  EmailShareButton,
  EmailIcon,
  FacebookShareButton,
  FacebookIcon,
  LinkedinShareButton,
  LinkedinIcon,
  RedditShareButton,
  RedditIcon,
  TwitterShareButton,
  TwitterIcon,
  WhatsappShareButton,
  WhatsappIcon,
  WorkplaceShareButton,
  WorkplaceIcon
} from "react-share";

interface props {
  showModal: boolean;
  handleModal: () => void;
  title: string;
  getShareLink: any;
}

const ShareModal = ({ showModal, handleModal, title, getShareLink }: props) => {
  const [shareLink, setShareLink] = useState("");

  useEffect(() => {
    setShareLink(getShareLink);
    return () => {};
  }, [getShareLink]);

  return (
    <Modal show={showModal} onHide={handleModal}>
      <Modal.Header closeButton className="bg-secondary">
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="bg-secondary">
        <Row className="align-items-center justify-content-center px-0">
        <Col lg={1} xs={1}>
            <FacebookShareButton
              url={shareLink}
              quote={"Check this kid's drawing animation."}
              className="mr-3"
            >
              <FacebookIcon size={32} round />
            </FacebookShareButton>
          </Col>
          <Col lg={1} xs={1}>
            <WhatsappShareButton
              url={shareLink}
              title={title}
              separator=":: "
              className="mr-2"
            >
              <WhatsappIcon size={32} round />
            </WhatsappShareButton>
          </Col>
          <Col lg={1} md={1} xs={1}>
            <TwitterShareButton
              url={shareLink}
              title={"Check this kid's drawing animation."}
              className="mr-2"
            >
              <TwitterIcon size={32} round />
            </TwitterShareButton>
          </Col>
          <Col lg={1} xs={1}>
            <LinkedinShareButton
              url={shareLink}
              className="mr-2"
            >
              <LinkedinIcon size={32} round />
            </LinkedinShareButton>
          </Col>
          <Col lg={1} xs={1}>
            <EmailShareButton
              url={shareLink}
              subject={"Check this kid's drawing animation."}
              body="body"
              className="mr-2"
            >
              <EmailIcon size={32} round />
            </EmailShareButton>
          </Col>
          <Col lg={1} xs={1}>
            <RedditShareButton
              url={shareLink}
              title={"Check this kid's drawing animation."}
              windowWidth={660}
              windowHeight={460}
              className="mr-2"
            >
              <RedditIcon size={32} round />
            </RedditShareButton>
          </Col>
          <Col lg={1} xs={1}>
          <WorkplaceShareButton
            url={shareLink}
            quote={"Check this kid's drawing animation."}
            className="mr-2"
          >
            <WorkplaceIcon size={32} round />
          </WorkplaceShareButton>
          </Col>
        </Row>
      </Modal.Body>
      <Modal.Footer className="bg-secondary">
        <Button variant="default" onClick={handleModal}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ShareModal;
