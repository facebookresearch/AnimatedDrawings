import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import "./assets/scss/root.scss";
import ResultsPage from "./containers/ResultsPage";
import MainPage from "./containers/MainPage";
import SharingPage from "./containers/SharingPage";

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
      </Switch>
    </Router>
  );
}

export default App;
