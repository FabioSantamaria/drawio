import React, { useEffect, useRef } from "react";
import { Streamlit } from "streamlit-component-lib";
import { Excalidraw, exportToBlob } from "@excalidraw/excalidraw";
import "@excalidraw/excalidraw/index.css";

export default function App({ args }) {
  const {
    width = 900,
    height = 520,
    readOnly = false,
    theme = "light",
    initialData = {},
    exportRequested = false,
  } = args || {};

  const apiRef = useRef(null);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (!initializedRef.current) {
      Streamlit.setComponentReady();
      initializedRef.current = true;
    }
    Streamlit.setFrameHeight(height);
  }, [height]);

  useEffect(() => {
    // Apply initial data once to avoid update loops
    if (initialData && apiRef.current && initialData.elements && !apiRef.current.__appliedInitial) {
      apiRef.current.updateScene(initialData);
      apiRef.current.__appliedInitial = true;
    }
  }, [initialData]);

  useEffect(() => {
    if (exportRequested && apiRef.current) {
      const elements = apiRef.current.getSceneElements();
      const appState = apiRef.current.getAppState();
      exportToBlob({ elements, appState, mimeType: "image/png" })
        .then((blob) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const dataUrl = reader.result;
            Streamlit.setComponentValue({ dataUrl });
          };
          reader.readAsDataURL(blob);
        })
        .catch((err) => {
          Streamlit.setComponentValue({ error: String(err) });
        });
    }
  }, [exportRequested]);

  return (
    <div style={{ width, height }}>
      <Excalidraw
        excalidrawAPI={(api) => (apiRef.current = api)}
        theme={theme}
        viewModeEnabled={readOnly}
        initialData={initialData}
      />
    </div>
  );
}