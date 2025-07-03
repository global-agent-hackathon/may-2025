import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '../../App';

const Sidepanel = () => {
  return (
    <div className="sidepanel-container">
      <header className="header">
      </header>
      <main className="main-content">
        <App />
      </main>
    </div>
  );
};

const container = window.document.querySelector('#app-container');
if (!container) {
  throw new Error('#app-container element not found');
}

const root = createRoot(container);
root.render(<Sidepanel />);

if (module.hot) module.hot.accept();
