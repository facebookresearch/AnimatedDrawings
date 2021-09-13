import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
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
          <MainPage />
        </Route>
        <Route exact path="/result/:uuid">
          <ResultsPage />
        </Route>
        <Route exact path="/share/:uuid/:type">
          <SharingPage />
        </Route>
        <Route exact path="/home">
          <HomePage />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
