# IGI Certificate Retrieval Automation

This project automates the process of retrieving certificate information from the IGI (International Gemological Institute) website.

## Features

- Automatically navigates to the IGI certificate verification page
- Handles Cloudflare protection
- Inputs certificate numbers and extracts data
- Saves results to Excel files
- Supports batch processing of multiple certificate numbers

## Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. **Update certificate numbers**: Edit the `certificate_numbers` list in `certificate_automation.py` or `test_automation.py` with your actual certificate numbers.

2. **Run the automation**:
```bash
python3 certificate_automation.py
```

Or for testing:
```bash
python3 test_automation.py
```

### Configuration

The main configuration is in the `main()` function:

```python
# Configuration
website_url = "https://www.igi.org/verify-your-report/"
excel_file_path = "certificate_data.xlsx"

# List of certificate numbers to process
certificate_numbers = [
    "CERT001",
    "CERT002",
    "CERT003",
    # Add more certificate numbers as needed
]
```

## Website Structure

The automation is configured for the IGI certificate verification page with the following elements:

- **Input Field**: `name="r"` with placeholder "Enter Your Report No."
- **Submit Button**: Button containing text "Verify"
- **Form Action**: `https://www.igi.org/verify-your-report/`

## Features

### Cloudflare Protection Handling
The script automatically waits for Cloudflare protection to clear before proceeding.

### Error Handling
- Graceful handling of missing elements
- Timeout protection for slow-loading pages
- Detailed error logging

### Data Extraction
The script extracts the following information (selectors may need adjustment based on actual result page structure):
- Certificate Number
- Holder Name
- Issue Date
- Expiry Date
- Status

## Output

Results are saved to an Excel file with the following columns:
- certificate_number
- holder_name
- issue_date
- expiry_date
- status

## Notes

- The script includes delays between requests to be respectful to the server
- Some selectors for data extraction may need adjustment based on the actual result page structure
- The script runs in non-headless mode by default for debugging purposes

## Troubleshooting

1. **ChromeDriver issues**: Make sure Chrome browser is installed and up to date
2. **Cloudflare timeout**: Increase the `max_wait_time` in the `wait_for_cloudflare()` method
3. **Element not found**: Check if the website structure has changed and update selectors accordingly

## Legal Notice

This automation tool is for educational purposes. Please ensure compliance with IGI's terms of service and respect rate limiting when using this tool. 