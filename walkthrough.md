# VERA - Walkthrough

## 1. Installation

First, ensure you have Python 3.13 installed. Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

> [!NOTE]
> If `google-adk` is not found in PyPI (as it might be a private or preview package), you may need to install it from a local wheel or specific index provided in the course materials.

## 2. Running Tests

Once dependencies are installed, you can verify the system by running the tests:

```bash
python -m unittest discover tests
```

## 3. Running the Application

To start the VERA interface, use the python executable from the virtual environment and set the PYTHONPATH:

```bash
PYTHONPATH=. .venv/bin/streamlit run vera/main.py
```

## 4. Usage

1.  **API Key:** Enter your Google API Key in the sidebar.
2.  **Model:** Select the Gemini model you wish to use.
3.  **Investigate:** Paste a text or URL into the main input box and click "Analyze & Verify".
4.  **Results:** VERA will display the progress and the final report.

## 5. Architecture Overview

-   **`vera/main.py`**: The Streamlit frontend. Handles user session and runs the ADK Runner asynchronously.
-   **`vera/agents.py`**: Defines the 3-Agent system (Coordinator, Researcher, Analyst).
-   **`vera/tools.py`**: Contains the `search_tool` using DuckDuckGo.
