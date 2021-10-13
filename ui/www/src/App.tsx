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
import AboutPage from "./containers/AboutPage";

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <HomePage />
        </Route>
        <Route path="/about">
          <AboutPage />
        </Route>
        <Route path="/canvas">
          <MainPage />
        </Route>
        <Route path="/share/:uuid/:type">
          <SharingPage />
        </Route>
        <Redirect from="*" to="/" />
      </Switch>
    </Router>
  );
}

export default App;
