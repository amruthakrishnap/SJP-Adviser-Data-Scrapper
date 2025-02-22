# Adviser Info Scraper

This script scrapes adviser information from the St. James's Place website, specifically from the 'Find an Adviser' page. It extracts various details such as profile image, adviser name, organization, phone number, email, website, and locations. The results are saved to a CSV file.

## Prerequisites

- Python 3.7+
- Pip (Python package installer)

## Installation

1. **Clone the repository** (or download the script).

    ```bash
    git clone https://github.com/amruthakrishnap/SJP-Adviser-Data-Scrapper
    cd SJP-Adviser-Data-Scrapper
    ```

2. **Create and activate a virtual environment** (optional but recommended).

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies**.

    ```bash
    pip install -r requirements.txt
    playwright install
    ```

## Usage

1. **Run the script**.

    ```bash
    python main.py
    ```

2. **Follow the prompt** to enter the keyword for the location search.

    ```plaintext
    Enter Full KeyWord: [Type the location keyword and press Enter]
    Example : "Bath UK" , "London UK" , "Exeter UK"
    ```

3. **The script will automatically navigate** to the St. James's Place website
   ```plaintext
    You will get each script running status..!
    Once the Scrapping get's over data will save to adviser_info.csv
    ```
