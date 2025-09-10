import streamlit as st
from component.monaco_component import monaco_editor
from html import escape
import markdown
import difflib
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    import openai
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
except Exception:
    openai = None

st.set_page_config(layout="wide", page_title="Monaco Streamlit Editor — Selection + LLM")

st.title("Monaco-powered editor — true cursor selection + block instructions")

# initialize text
if "text" not in st.session_state:
    st.session_state.text = (
        "# Example Document\n\nThis is a sample Markdown document.\n\n- Bullet one\n- Bullet two\n\nSome paragraph text to edit.\n\n## Section Two\nMore lines here.\n"
    )
if "edited_text" not in st.session_state:
    st.session_state.edited_text = st.session_state.text
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.history_index = -1
if "last_suggestion" not in st.session_state:
    st.session_state.last_suggestion = ""

# Layout
left, right = st.columns([1,1])

with left:
    st.subheader("Editor (Monaco)")
    st.caption("Select text with mouse — selection info is passed back to Python.")
    comp = monaco_editor(value=st.session_state.edited_text, key="monaco1", language="markdown", theme="vs-light")

    if comp and "selection" in comp:
        sel = comp["selection"]
        start = sel["startIndex"]
        end = sel["endIndex"]
        start_line = sel["startLine"]
        end_line = sel["endLine"]
        st.markdown(f"**Selection:** {start} → {end} (lines {start_line} → {end_line})")
        full_text = comp.get("value", st.session_state.edited_text)
        selected_block = full_text[start:end] if (start is not None and end is not None and end > start) else ""
    else:
        selected_block = ""

    st.markdown("---")
    st.subheader("Instruction (tooltip)")
    instruction = st.text_input("Write instruction to modify the selected block", value="Improve clarity and fix grammar (keep Markdown).")

    st.markdown("")
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Apply instruction (LLM)"):
            if not selected_block.strip():
                st.warning("No text selected. Select a region in the Monaco editor and try again.")
            else:
                if not OPENAI_API_KEY or openai is None:
                    st.error("OPENAI_API_KEY not set. Set it to call LLM.")
                else:
                    system = (
                        "You are a Markdown editor assistant. Given a selection and an instruction, "
                        "return ONLY the edited selection in Markdown format. Do not add extra commentary."
                    )
                    user_prompt = f"Instruction: {instruction}\n\nSelected block:\n{selected_block}\n\nReturn only the edited block in Markdown."
                    try:
                        resp = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.2,
                            max_tokens=512
                        )
                        suggestion = resp.choices[0].message["content"].strip()
                    except Exception as e:
                        st.error(f"LLM error: {e}")
                        suggestion = ""

                    if suggestion:
                        st.session_state.history = st.session_state.history[: st.session_state.history_index + 1]
                        st.session_state.history.append(st.session_state.edited_text)
                        st.session_state.history_index = len(st.session_state.history) - 1

                        new_text = full_text[:start] + suggestion + full_text[end:]
                        st.session_state.edited_text = new_text
                        st.session_state.last_suggestion = suggestion
                        st.success("Applied LLM suggestion to selected block. See preview on right.")
    with c2:
        if st.button("Apply instruction (local simple)"):
            if not selected_block.strip():
                st.warning("No selection.")
            else:
                if "uppercase" in instruction.lower():
                    replaced = selected_block.upper()
                elif "lowercase" in instruction.lower():
                    replaced = selected_block.lower()
                elif "remove" in instruction.lower() or "delete" in instruction.lower():
                    replaced = ""
                else:
                    st.info("No simple local action matched. Try LLM or use a different instruction.")
                    replaced = selected_block

                st.session_state.history = st.session_state.history[: st.session_state.history_index + 1]
                st.session_state.history.append(st.session_state.edited_text)
                st.session_state.history_index = len(st.session_state.history) - 1

                new_text = full_text[:start] + replaced + full_text[end:]
                st.session_state.edited_text = new_text
                st.success("Applied local change to selection.")
    with c3:
        if st.button("Reset editor to original"):
            st.session_state.edited_text = st.session_state.text
            st.success("Reset.")

with right:
    st.subheader("Edited text (highlights)")
    orig = st.session_state.text
    edited = st.session_state.edited_text

    def make_html_diff(orig: str, edited: str) -> str:
        sm = difflib.SequenceMatcher(None, orig, edited)
        html_orig = []
        html_edited = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            a = escape(orig[i1:i2])
            b = escape(edited[j1:j2])
            if tag == "equal":
                html_orig.append(a)
                html_edited.append(b)
            elif tag == "replace":
                if a:
                    html_orig.append(f'<span class="del">{a}</span>')
                if b:
                    html_edited.append(f'<span class="ins">{b}</span>')
            elif tag == "delete":
                if a:
                    html_orig.append(f'<span class="del">{a}</span>')
            elif tag == "insert":
                if b:
                    html_edited.append(f'<span class="ins">{b}</span>')
        css = """                <style>
          .diff-wrap { display:flex; gap:12px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
          .col { width:50%; padding:12px; box-sizing:border-box; border:1px solid #eee; border-radius:6px; background:#fff; overflow:auto; max-height:600px;}
          .ins { background-color: #e6ffed; color: #042000; }
          .del { background-color: #ffecec; color: #4a0000; text-decoration: line-through; }
          pre { white-space: pre-wrap; word-wrap: break-word; font-family:inherit; }
        </style>
        """                html = css + '<div class="diff-wrap>'
        html += '<div class="col"><h4>Original</h4><pre>' + ''.join(html_orig) + '</pre></div>'
        html += '<div class="col"><h4>Edited</h4><pre>' + ''.join(html_edited) + '</pre></div>'
        html += '</div>'
        return html

    st.components.v1.html(make_html_diff(orig, edited), height=520, scrolling=True)

    st.markdown("---")
    st.subheader("Rendered Edited Markdown")
    st.components.v1.html(markdown.markdown(edited or "", extensions=["fenced_code", "tables", "nl2br"]), height=350, scrolling=True)

    st.markdown("---")
    col_undo, col_commit, col_download = st.columns([1,1,1])
    with col_undo:
        if st.button("Undo"):
            if st.session_state.history_index >= 0 and st.session_state.history:
                st.session_state.edited_text = st.session_state.history[st.session_state.history_index]
                st.session_state.history_index -= 1
                st.success("Undid last change.")
            else:
                st.warning("No history.")
    with col_commit:
        if st.button("Commit edited to original"):
            st.session_state.text = st.session_state.edited_text
            st.success("Committed.")
    with col_download:
        st.download_button("Download Edited .md", st.session_state.edited_text, "edited.md", "text/markdown")
