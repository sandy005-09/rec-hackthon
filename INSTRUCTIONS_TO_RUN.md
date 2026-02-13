# How to Run GenAI Financial Assistant

Since Python is not installed on this machine, you need to perform the following steps manually:

1.  **Install Python**
    -   Download Python from https://www.python.org/downloads/
    -   **IMPORTANT:** Check the box **"Add Python to PATH"** in the installer.

2.  **Configure API Key**
    -   Open the `.env` file in this directory.
    -   Replace `your_key_here` with your valid Gemini API Key.
    -   Save the file.

3.  **Run the App**
    -   Double-click the `run_app.bat` file I created.
    -   Or, run the following commands in your terminal:
        ```bash
        pip install -r requirements.txt
        uvicorn main:app --reload
        ```

4.  **Access the Dashboard**
    -   Open http://127.0.0.1:8000 in your browser.
    -   Click "Overspending", "Bill Pay" or "Monthly Summary" to see the notifications.
