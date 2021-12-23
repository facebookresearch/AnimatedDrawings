import React, { useCallback, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";
import "./assets/scss/root.scss";
import MainPage from "./containers/MainPage";
import SharingPage from "./containers/SharingPage";
import HomePage from "./containers/HomePage";
import TermsPage from "./containers/TermsPage";
import AboutPage from "./containers/AboutPage";
import CookieBanner from "./components/Banners/CookieBanner";
import * as ReactGA from "react-ga4";
import { getCookieConsentValue } from "react-cookie-consent";

function App() {
  // Enable analytics if cookie accepted
  const handleAcceptCookie = useCallback(() => {
    if (process.env.REACT_APP_GOOGLE_ANALYTICS_ID) {
      if (process.env.NODE_ENV === "production") {
        console.log("*** INIT GA ***");

        ReactGA.default.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_ID);
      }
    }
  }, []);

  useEffect(() => {
    const isConsent = getCookieConsentValue("animated_drawings");
    if (isConsent === "true") {
      handleAcceptCookie();
    }
  }, [handleAcceptCookie]);

  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <HomePage />
        </Route>
        <Route path="/canvas">
          <MainPage />
        </Route>
        <Route path="/share/:videoId/:type">
          <SharingPage />
        </Route>
        <Route path="/terms">
          <TermsPage />
        </Route>
        <Route path="/about">
          <AboutPage />
        </Route>
        <Redirect from="*" to="/" />
      </Switch>
      <CookieBanner onAccept={handleAcceptCookie} />
    </Router>
  );
}

export default App;
