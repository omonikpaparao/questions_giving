import streamlit as st
import pandas as pd
import requests
import base64
from io import BytesIO

# GitHub repo details
GITHUB_REPO = st.secrets["github"]["username"]+"/sai"
GITHUB_FILE_PATH = "quiz_data.xlsx"
GITHUB_TOKEN = st.secrets["api"]["key"]  # Replace with your new secure GitHub token


def save_to_github_excel(df):
    """Save the quiz data as an Excel file and upload it to GitHub with proper formatting."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    # Convert DataFrame to Excel with text wrapping
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Quiz Data")

        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets["Quiz Data"]

        # Define a format with text wrapping enabled
        wrap_format = workbook.add_format({"text_wrap": True})

        # Apply text wrapping to all columns
        for col_num, col_name in enumerate(df.columns):
            worksheet.set_column(col_num, col_num, 30, wrap_format)  # Adjust width as needed

    excel_buffer.seek(0)

    # Encode Excel file in base64 for GitHub upload
    encoded_content = base64.b64encode(excel_buffer.read()).decode()

    # Check if file exists on GitHub
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    payload = {
        "message": "Updating quiz data",
        "content": encoded_content,
        "sha": sha  # Required if updating an existing file
    }

    # Push data to GitHub
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        return True
    else:
        st.error(f"GitHub API Error: {response.json()}")
        return False


def create_excel_download_link(df):
    """Create a download link for the generated Excel file."""
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Quiz Data")

        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets["Quiz Data"]

        # Define a format with text wrapping enabled
        wrap_format = workbook.add_format({"text_wrap": True})

        # Apply text wrapping to all columns
        for col_num, col_name in enumerate(df.columns):
            worksheet.set_column(col_num, col_num, 30, wrap_format)  # Adjust width as needed

    excel_buffer.seek(0)

    # Encode file to base64
    b64 = base64.b64encode(excel_buffer.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="quiz_data.xlsx">Download Excel File</a>'
    return href


def main():
    st.title("Dynamic Quiz Generator")

    num_questions = st.number_input("Enter the number of questions:", min_value=1, step=1)

    quiz_data = []
    for i in range(int(num_questions)):
        st.subheader(f"Question {i + 1}")
        question = st.text_area(f"Enter question {i + 1}")  # Supports multi-line input

        options = []
        for j in range(4):
            options.append(st.text_input(f"Option {j + 1} for Question {i + 1}"))

        correct_answer = st.text_input(f"Correct answer for Question {i + 1}")

        quiz_data.append({
            "Question": question,
            "Option 1": options[0] if len(options) > 0 else "",
            "Option 2": options[1] if len(options) > 1 else "",
            "Option 3": options[2] if len(options) > 2 else "",
            "Option 4": options[3] if len(options) > 3 else "",
            "Correct Answer": correct_answer
        })

    if st.button("Submit"):
        if len(quiz_data) > 0:
            df = pd.DataFrame(quiz_data)

            if save_to_github_excel(df):
                st.success("Quiz data successfully saved to GitHub in Excel format!")
                st.markdown(create_excel_download_link(df), unsafe_allow_html=True)
            else:
                st.error("Failed to save data to GitHub.")
        else:
            st.warning("Please enter at least one question before submitting.")


if __name__ == "__main__":
    main()
