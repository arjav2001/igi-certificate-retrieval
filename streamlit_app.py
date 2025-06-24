import streamlit as st
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Extraction logic (reuse from previous script, simplified for Streamlit)
def setup_driver(download_dir):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_fields_from_page(driver, cert_number):
    time.sleep(2)
    visible_text = driver.find_element(By.TAG_NAME, "body").text
    lines = [line.strip() for line in visible_text.split('\n') if line.strip()]
    def get_next_line(label):
        for i, line in enumerate(lines):
            if label in line:
                if i + 1 < len(lines):
                    return lines[i + 1]
        return "Not found"
    return {
        'REPORT': cert_number,
        'SHAPE': get_next_line("Shape and Cutting Style").split(" ")[0],
        'CTS': get_next_line("Carat Weight").split(" ")[0],
        'COLOR': get_next_line("Color Grade"),
        'CLARITY': get_next_line("Clarity Grade").replace(" ", "")
    }

def go_to_certificate(driver, cert_number):
    # Navigate using the IGI internal form
    try:
        # Always go to the main verify page
        driver.get("https://www.igi.org/verify-your-report/")
        # Wait for input
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "r"))
        )
        input_box = driver.find_element(By.NAME, "r")
        input_box.clear()
        input_box.send_keys(cert_number)
        # Click the Verify button
        verify_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify')]")
        verify_btn.click()
        # Wait for the PDF Report tab to appear
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'PDF Report')]") )
        )
        return True
    except Exception as e:
        st.warning(f"Error navigating to certificate {cert_number}: {e}")
        return False

def main():
    st.title("IGI Certificate Data Extractor")
    st.write("Enter a new-line-separated list of certificate numbers below. After passing the Cloudflare check in the browser, click 'Continue after Cloudflare check'.")
    cert_input = st.text_area("Certificate Numbers", "")
    if 'driver' not in st.session_state:
        st.session_state['driver'] = None
    if 'extraction_ready' not in st.session_state:
        st.session_state['extraction_ready'] = False
    start = st.button("Start Extraction")
    if start and st.session_state['driver'] is None:
        with st.spinner("Launching browser. Please pass the Cloudflare check if prompted."):
            driver = setup_driver(os.getcwd())
            driver.get("https://www.igi.org/verify-your-report/")
            st.session_state['driver'] = driver
            st.session_state['extraction_ready'] = False
    if st.session_state['driver'] is not None and not st.session_state['extraction_ready']:
        st.info("If you see a Cloudflare check, please complete it in the browser window. Then return here and click 'Continue after Cloudflare check'.")
        if st.button("Continue after Cloudflare check"):
            st.session_state['extraction_ready'] = True
    if st.session_state['driver'] is not None and st.session_state['extraction_ready']:
        cert_numbers = [c.strip() for c in cert_input.splitlines() if c.strip()]
        if not cert_numbers:
            st.error("Please enter at least one certificate number.")
            return
        results = []
        for idx, cert_number in enumerate(cert_numbers):
            st.write(f"Processing {cert_number} ({idx+1}/{len(cert_numbers)})...")
            if go_to_certificate(st.session_state['driver'], cert_number):
                data = extract_fields_from_page(st.session_state['driver'], cert_number)
                results.append(data)
                st.success(f"Extracted data for {cert_number}")
            else:
                st.error(f"Failed to process {cert_number}")
        st.session_state['driver'].quit()
        st.session_state['driver'] = None
        st.session_state['extraction_ready'] = False
        if results:
            df = pd.DataFrame(results)
            st.write(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="igi_certificates.csv",
                mime="text/csv"
            )
        else:
            st.error("No data extracted.")

if __name__ == "__main__":
    main() 