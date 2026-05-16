# AI Startup Orchestrator

The **AI Startup Orchestrator** is an intelligent tool designed to streamline the early stages of startup planning and analysis. It acts as an interactive assistant, conducting a guided interview with the founder to gather essential details about the problem, target audience, competitors, business model, and Minimum Viable Product (MVP) idea. Once the initial data is collected, a suite of automated agents performs in-depth analysis to provide actionable insights.

## Features

- **Guided Founder Interview**: An interactive chat interface to gather structured information about your startup idea.
- **Market Analysis Engine**: Evaluates the target niche and competitors using web research, estimating TAM, SAM, SOM, CAGR, and market density (Blue vs. Red Ocean).
- **Financial Analysis Engine**: Projects key financial metrics including LTV/CAC ratio, capital intensity, an overall investability score, and highlights potential red flags.
- **MVP Architecture Engine**: Generates a concrete 4-week founder sprint plan based on the startup's complexity, time-to-market, core features to focus on, and recommended tech stack.
- **Bilingual Interface**: Seamlessly switch the UI between English and Turkish.

## Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Data Visualization**: [Plotly](https://plotly.com/)
- **Search Integration**: [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)
- **Data Storage**: Local JSON storage (for MVP stage)

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd Start-Up-AI-R
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the provided local URL (usually `http://localhost:8501`) in your browser.
2. Select your preferred language (English or Turkish) from the sidebar.
3. Answer the 5 core startup questions in the chat interface.
4. Once completed, your data will be saved.
5. Click on the respective buttons to run the **Market Analysis**, **Financial Analysis**, or **MVP Roadmap** generation.
6. Review your personalized, data-driven startup dashboards.
