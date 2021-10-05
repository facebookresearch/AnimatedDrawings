import React from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import "./assets/scss/root.scss";
import ResultsPage from "./containers/ResultsPage";
import MainPage from "./containers/MainPage";
import SharingPage from "./containers/SharingPage";
import HomePage from "./containers/HomePage";

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
        <Route path="/result/:uuid">
          <ResultsPage />
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
