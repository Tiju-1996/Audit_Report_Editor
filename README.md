# streamlit-monaco-editor

A Streamlit app embedding the Monaco editor as a custom component, providing true cursor-based selection and the ability to apply instruction-based edits (via LLM or simple local transforms) to the selected block.

## What you get
- Monaco editor in the browser (true cursor/selection info sent to Python).
- Instruction input (tooltip-like) to modify selected text only.
- LLM integration (OpenAI) to rewrite the selected block and replace it in the document.
- Side-by-side highlighted diff: additions (green) and deletions (red/strikethrough).
- Undo history and export as `.md`.

## Build & Run
1. Create a Python virtual environment and install Python deps:

```bash
python -m venv venv
source venv/bin/activate   # on Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

2. Build the frontend bundle (Node + npm required):

```bash
cd frontend
npm install
npm run build
cd ..
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

4. Open the URL shown (usually http://localhost:8501).

## Notes
- During development you can set `_RELEASE = False` (already set) so the component serves static files from `frontend/dist`.
- To develop the frontend, use `npm run dev` in the frontend directory and adjust `declare_component` to point to the dev server if needed.
- Set `OPENAI_API_KEY` in environment (or `.env`) to enable LLM-powered edits.
