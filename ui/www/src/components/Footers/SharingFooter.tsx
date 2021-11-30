import React from "react";
import { Navbar, Nav } from "react-bootstrap";

interface props {
  uuid?: string;
  setShowModal: (res: boolean) => void;
}

export default function SharingFooter({ uuid, setShowModal }: props) {
  return (
    <Navbar expand="sm" bg="transparent" className="align-items-start">
      <Nav className="mr-auto">
        <Nav.Link onClick={() => setShowModal(true)} className="text-primary">
          About This Demo
        </Nav.Link>
        <Nav.Link
          href={`https://docs.google.com/forms/d/e/1FAIpQLSfynXUEVc0YvSYGXN3BCFjl7uNthyEkxqibsNHn3pqA_Wt8Hg/viewform?entry.1387562397=${
            uuid !== "" ? uuid : "Preload Step [No ID]"
          }`}
          target="_blank"
          rel="noreferrer"
          className="text-primary"
        >
          Feedback
          <i className="bi bi-info-circle-fill ml-2 h3"></i>
        </Nav.Link>
        <Nav.Link
          href={`https://docs.google.com/forms/d/e/1FAIpQLSeKewkuKtcePdGLAbzkjF6apnLHpfswMyjgt7hKBNH0m02W3Q/viewform?usp=pp_url&entry.1352936659=${window.location.href}`}
          target="_blank"
          rel="noreferrer"
          className="text-primary"
        >
          Report
        </Nav.Link>
      </Nav>
      <Nav className="text-right">
        <Nav.Link
          href="https://www.facebook.com/about/privacy/"
          target="_blank"
          rel="noreferrer"
          className="text-primary"
        >
          Privacy Policy
        </Nav.Link>
        <Nav.Link
          href="https://www.facebook.com/policies_center"
          target="_blank"
          rel="noreferrer"
          className="text-primary"
        >
          Terms
        </Nav.Link>
        <Nav.Link
          href="https://www.facebook.com/policies/cookies/"
          target="_blank"
          rel="noreferrer"
          className="text-primary"
        >
          Cookies
        </Nav.Link>
      </Nav>
    </Navbar>
  );
}
