import React from 'react';
import './App.css';
import ClinicalTrialMatcher from './ClinicalTrialMatcher';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Clinical Trial Matching Demo</h1>
      </header>
      <main>
        <ClinicalTrialMatcher />
      </main>
    </div>
  );
}

export default App;