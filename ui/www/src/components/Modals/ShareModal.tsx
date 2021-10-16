import React, { useRef, useState, useEffect } from "react";
import { Modal, Row, Col, FormControl, Badge } from "react-bootstrap";
import DownloadIcon from "../../assets/customIcons/downloadIcon.svg";
import FacebookIcon from "../../assets/customIcons/facebookIcon.svg";
import TwitterIcon from "../../assets/customIcons/twitterIcon.svg";
import WhatsappIcon from "../../assets/customIcons/whatsapp.svg";
import EmailIcon from "../../assets/customIcons/envelopeIcon.svg";
import {
  EmailShareButton,
  FacebookShareButton,
  TwitterShareButton,
  WhatsappShareButton,
} from "react-share";

interface props {
  showModal: boolean;
  title: string;
  getShareLink: any;
  videoDownload: string; //base64
  handleModal: () => void;
}

const ShareModal = ({
  showModal,
  title,
  getShareLink,
  videoDownload,
  handleModal,
}: props) => {
  const [shareLink, setShareLink] = useState("");
  const [copySuccess, setCopySuccess] = useState("");
  const textAreaRef = useRef() as React.MutableRefObject<HTMLInputElement>;

  useEffect(() => {
    setShareLink(getShareLink);
    setCopySuccess("");
    return () => {};
  }, [getShareLink]);

  const copyToClipboard = (e: MouseEvent | any) => {
    textAreaRef.current.select();
    document.execCommand("copy");
    e.target.focus();
    setCopySuccess("Copied to clipboard!");
  };

  return (
    <Modal centered size="lg" show={showModal} onHide={handleModal}>
      <Modal.Header closeButton className="bg-secondary mt-lg-2">
        <h2 className="ml-lg-4 modal-title">SHARE</h2>
      </Modal.Header>
      <Modal.Body className="bg-secondary modal-share">
        <Row className="align-items-center pl-3 px-lg-5 mb-4">
          <Col lg={2} xs={2} className="px-0">
            <a
              download="animation.mp4"
              href={videoDownload}
              target="_blank"
              rel="noreferrer"
            >
              <img src={DownloadIcon} alt="icon" />
            </a>
          </Col>
          <Col lg={2} xs={2} className="px-0">
            <FacebookShareButton
              url={shareLink}
              quote={"Check this kid's drawing animation."}
              className="mr-3"
            >
              <img src={FacebookIcon} alt="icon" />
            </FacebookShareButton>
          </Col>
          <Col lg={2} xs={2} className="px-0">
            <WhatsappShareButton
              url={shareLink}
              title={title}
              separator=":: "
              className="mr-2"
            >
              <img src={WhatsappIcon} alt="icon" />
            </WhatsappShareButton>
          </Col>
          <Col lg={2} xs={2} className="px-0">
            <TwitterShareButton
              url={shareLink}
              title={"Check this kid's drawing animation."}
              className="mr-2"
            >
              <img src={TwitterIcon} alt="icon" />
            </TwitterShareButton>
          </Col>
          <Col lg={2} xs={2} className="px-0">
            <EmailShareButton
              url={shareLink}
              subject={"Check this kid's drawing animation."}
              body="body"
              className="mr-2"
            >
              <img src={EmailIcon} alt="icon" />
            </EmailShareButton>
          </Col>
        </Row>
        <Row className="px-lg-4 mt-2 mb-1">
          <Col>
            <h6>PAGE LINK</h6>
          </Col>
        </Row>
        <Row className="align-items-center mt-3 px-lg-4">
          <Col lg={11} md={11} xs={10}>
            <FormControl
              aria-describedby="basic-addon1"
              ref={textAreaRef}
              type="text"
              readOnly
              value={shareLink}
            />
          </Col>
          <Col
            lg={1}
            md={1}
            xs={1}
            style={{ cursor: "pointer" }}
            onClick={copyToClipboard}
          >
            <i className="bi bi-link-45deg h1"></i>
          </Col>
        </Row>
        <Row className="px-lg-4">
          <Col lg={2} className="mt-1 h4">
            <Badge variant="success">{copySuccess}</Badge>
          </Col>
        </Row>
      </Modal.Body>
      <Modal.Footer className="bg-secondary"></Modal.Footer>
    </Modal>
  );
};

export default ShareModal;
