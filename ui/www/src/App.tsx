import React from "react";
import HomePage from "./containers/HomePage";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import ResultsPage from "./containers/ResultsPage";

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/result/:uuid">
          <ResultsPage />
        </Route>
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
