import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Capture render errors for debugging
window.onerror = (message, source, lineno, colno, error) => {
  console.error("GLOBAL ERROR:", message, source, `line ${lineno}:${colno}`, error?.stack);
};

window.onunhandledrejection = (event) => {
  console.error("UNHANDLED REJECTION:", event.reason);
};

try {
  const rootEl = document.getElementById("root");
  if (!rootEl) {
    console.error("ERROR: #root element not found in DOM");
  } else {
    console.log("Mounting React app...");
    ReactDOM.createRoot(rootEl).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
    console.log("React app mounted successfully");
  }
} catch (e) {
  console.error("FATAL MOUNT ERROR:", e);
}