%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#1f2937', 'edgeLabelBackground': '#1e1e1e', 'fontSize': '14px', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart TD
    A[User Access] --> B[Authentication (Optional)]
    B --> C[Feedback Submission]
    C --> D[Sentiment Analysis (VADER → TextBlob → Fallback)]
    D --> E[Database Storage with Analysis Results]
    E --> F[Real-Time Dashboard Updates]
    F --> G[Email Notification (Negative Feedback)]
    G --> H[Admin Review & Action]
