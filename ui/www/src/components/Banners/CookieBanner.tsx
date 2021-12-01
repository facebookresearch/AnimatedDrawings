import React from "react";
import CookieConsent from "react-cookie-consent";

const CookieBanner = () => {
  return (
    <CookieConsent
      style={{
        padding: "12px",
        backgroundColor: "white",
        color: "black",
        fontSize: "14px",
      }}
      overlay
      disableButtonStyles
      buttonText="Accept"
      cookieName="animated_drawings"
      buttonClasses="btn btn-info accept-button"
    >
      This demo uses cookies to enhance the user experience, and allow us to
      remember you. To find out more about the cookies we use, see our{" "}
      <a
        href="https://www.facebook.com/policies/cookies/"
        target="_blank"
        rel="noreferrer"
      >
        <b>Privacy Policy</b>
      </a>{" "}
      and{" "}
      <a
        href="https://www.facebook.com/policies/cookies/"
        target="_blank"
        rel="noreferrer"
      >
        <b>Cookies.</b>
      </a>
    </CookieConsent>
  );
};

export default CookieBanner;
