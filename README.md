Let's take a step-by-step approach to help you set up the Stock Charting App using VS Code. We will ensure Python is installed correctly, clone the repository, and get the app running. We will also clean up any potential issues caused by previous steps.

## Step 1: Verify and Clean Up Python Installation

1. **Uninstall Python (if needed)**:
   - Open Control Panel and go to "Uninstall a program".
   - Uninstall any existing Python installations.

2. **Reinstall Python**:
   - Download Python from the [official Python website](https://www.python.org/downloads/).
   - Run the installer and make sure to check the box that says "Add Python to PATH".
   - Select "Install Now" and follow the on-screen instructions.

3. **Verify Installation**:
   - Open Command Prompt or PowerShell.
   - Verify Python installation:
     ```sh
     python --version
     ```
     Ensure it displays your Python version (e.g., Python 3.8.10).

   - Verify Pip installation:
     ```sh
     pip --version
     ```
     Ensure it displays the Pip version (e.g., pip 21.1.1).

## Step 2: Install VS Code

1. **Download and Install VS Code**:
   - Download Visual Studio Code from the [official website](https://code.visualstudio.com/).
   - Install VS Code following the installation prompts.

## Step 3: Clone the Repository

1. **Open Command Prompt or PowerShell**:
   - Create a project directory:
     ```sh
     mkdir stock_charting_app
      ```
      ```sh
     cd stock_charting_app
     ```

2. **Clone the repository**:
   ```sh
   git clone https://github.com/mxmdgames/stonkape.git .
   ```

## Step 4: Open Project in VS Code

1. **Open VS Code**.
2. **Open the Project Folder**:
   - Click `File` > `Open Folder`.
   - Navigate to your `stock_charting_app` directory and select it.
   - Click "Select Folder" to open the project.

## Step 5: Install Required Packages

1. **Open the terminal in VS Code**:
   - Click on `Terminal` > `New Terminal`.
   
2. **Install the necessary packages**:
   ```sh
   pip install streamlit yfinance pandas plotly ta
   ```

## Step 6: Run the Streamlit App

1. **In the terminal, navigate to your project directory if not already there**:
   ```sh
   cd stock_charting_app
   ```

2. **Run the Streamlit app**:
   ```sh
   streamlit run stock_charting_app2.py
   ```

## Troubleshooting

### Python or Pip Command Not Found

- **Symptom**: Running `python --version` or `pip --version` returns a "command not found" error.
- **Solution**:
  1. Ensure Python and Pip are installed from the [official Python website](https://www.python.org/downloads/).
  2. Verify the installation paths are added to the system's PATH environment variable.

### Repository Cloning Issues

- **Symptom**: Cloning the repository fails.
- **Solution**:
  1. Ensure Git is installed by running `git --version`.
  2. Verify the URL is correct and try again.

### Package Installation Errors

- **Symptom**: Running `pip install` commands fail.
- **Solution**:
  1. Ensure you have an active internet connection.
  2. Check if you have permission to install packages globally; if not, run your terminal or command prompt as an administrator.

### Streamlit App Fails to Launch

- **Symptom**: Running `streamlit run stock_charting_app2.py` fails.
- **Solution**:
  1. Ensure all dependencies are correctly installed.
  2. Check for any syntax errors in `stock_charting_app2.py`.
  3. Review Streamlit error messages for specific issues.

### Port Already in Use

- **Symptom**: Error indicating the port is already in use.
- **Solution**:
  1. Stop any processes using the default Streamlit port (8501).
  2. Run Streamlit on a different port:
     ```sh
     streamlit run stock_charting_app2.py --server.port 8502
     ```

By following these steps and troubleshooting tips, you should be able to set up and run the Stock Charting App successfully. If you encounter further issues, consult the documentation or seek help from the community.
