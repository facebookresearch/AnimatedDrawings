import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import "./assets/scss/root.scss";
import ResultsPage from "./containers/ResultsPage";
import MainPage from "./containers/MainPage";

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/result/:uuid">
          <ResultsPage />
        </Route>
        <Route path="/">
          <MainPage />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
