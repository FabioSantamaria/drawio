import React from "react";
import { createRoot } from "react-dom/client";
import { withStreamlitConnection } from "streamlit-component-lib";
import App from "./App.jsx";

const Connected = withStreamlitConnection(App);

function mount() {
  const rootEl = document.getElementById("root");
  const root = createRoot(rootEl);
  root.render(<Connected />);
}

mount();