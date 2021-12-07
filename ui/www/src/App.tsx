import React from "react";
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
import PrivacyPolicyPage from "./containers/PrivacyPolicyPage";
import CookiePolicyPage from "./containers/CookiePolicyPage";
import CookieBanner from "./components/Banners/CookieBanner";

function App() {
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
        <Route path="/privacy">
          <PrivacyPolicyPage />
        </Route>
        <Route path="/cookies">
          <CookiePolicyPage />
        </Route>
        <Redirect from="*" to="/" />
      </Switch>
      <CookieBanner />
    </Router>
  );
}

export default App;
