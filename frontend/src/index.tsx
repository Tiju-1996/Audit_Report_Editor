import React, { useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import Editor from "@monaco-editor/react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

interface Props {
  value?: string;
  language?: string;
  theme?: string;
  options?: object;
}

const MonacoComponent = (props: Props) => {
  const { value = "", language = "markdown", theme = "vs-light", options = {} } = props as Props;
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;

    const sendState = () => {
      try {
        const model = editor.getModel();
        const fullText = model.getValue();
        const selection = editor.getSelection();
        const startPosition = model.getOffsetAt(selection.getStartPosition());
        const endPosition = model.getOffsetAt(selection.getEndPosition());

        const payload = {
          value: fullText,
          selection: {
            startLine: selection.startLineNumber,
            startColumn: selection.startColumn,
            endLine: selection.endLineNumber,
            endColumn: selection.endColumn,
            startIndex: startPosition,
            endIndex: endPosition
          }
        };
        Streamlit.setComponentValue(payload);
      } catch (e) {
        // ignore
      }
    };

    // send initial state
    sendState();

    editor.onDidChangeModelContent(() => {
      sendState();
    });

    editor.onDidChangeCursorSelection(() => {
      sendState();
    });
  };

  useEffect(() => {
    // noop: props updates handled by Streamlit reload
  }, []);

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <Editor
        height="80vh"
        defaultLanguage={language}
        defaultValue={value}
        theme={theme}
        options={{
          minimap: { enabled: false },
          wordWrap: "on",
          tabSize: 2,
          fontSize: 14,
          ...options
        }}
        onMount={handleEditorDidMount}
      />
    </div>
  );
};

const Wrapped = withStreamlitConnection(MonacoComponent);
const root = createRoot(document.getElementById("root")!);
root.render(<Wrapped />);
