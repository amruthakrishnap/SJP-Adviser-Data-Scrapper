import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time

async def scrape_adviser_info(url):
    async with async_playwright() as p:
        keyword = input("Enter Full KeyWord: ")
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(5)
        
        input_selector = await page.wait_for_selector("#edit-location")
        print("Got The Locator Yo ...! ")
        # Click on the input field
        await input_selector.click()
        print("CLicking the Locator cool ....! ")
        
        # Type the desired input
        await input_selector.fill(keyword)
        print("Added your KeyWord To Input Box ...!")
        
        await asyncio.sleep(5)
        
        # Press Enter
        await page.keyboard.press("ArrowDown")
        time.sleep(5)
        await page.keyboard.press("Enter")
        time.sleep(5)
        print("Scrapping Will start in a Minute....!")
        await page.keyboard.press("Enter")
        # Wait for some time to see the result (optional)
        await page.wait_for_timeout(5000) 
        await asyncio.sleep(30)
        async def print_search_info():
            result_count_selector = '.result-count.results-content'
            element = await page.query_selector(result_count_selector)
            if element:
                text = await element.text_content()
                print(text.strip())

        await print_search_info()
        
        all_data = []
        total_rows_fetched = 0

        async def extract_text(selector, element=None):
            element = element or page
            if selector:
                el = await element.query_selector(selector)
                if el:
                    text_content = await el.text_content()
                    return text_content.strip() if text_content else ''
            return ''

        async def extract_all_text(selector, element=None):
            element = element or page
            if selector:
                elements = await element.query_selector_all(selector)
                return [await extract_text('', el) for el in elements]
            return []

        async def scrape_current_page(page_number):
            nonlocal total_rows_fetched
            containers = await page.query_selector_all('.inner-advisors-wrapper')
            rows_fetched = len(containers)
            total_rows_fetched += rows_fetched
            print(f"Scraping page {page_number} with {rows_fetched} rows, total rows fetched: {total_rows_fetched}")

            for container in containers:
                try:
                    profile_image_element = await container.query_selector('.viewsers-advis-image img')
                    profile_image = await profile_image_element.get_attribute('src') if profile_image_element else ''
                    
                    adviser_name = await extract_text('.views-advisers-name', container)
                    adviser_org = await extract_text('.views-advisers-bio span:nth-of-type(2)', container)
                    
                    phone_numbers_set = set()
                    phone_elements = await container.query_selector_all('.views-advisers-phone a')
                    for phone_element in phone_elements:
                        phone_number = (await phone_element.text_content()).strip()
                        if "+ " not in phone_number:
                            phone_numbers_set.add(phone_number)
                    phone_numbers = '\n'.join(phone_numbers_set)

                    adviser_email_element = await container.query_selector('.views-advisers-email a')
                    adviser_email = (await adviser_email_element.text_content()).strip() if adviser_email_element else ''
                    adviser_website_element = await container.query_selector('.views-advisers-external-link a')
                    adviser_website = await adviser_website_element.get_attribute('href') if adviser_website_element else ''

                    # Extract main address
                    address_main_element = await container.query_selector('.views-advisers-address .location')
                    if address_main_element:
                        address_text = (await address_main_element.text_content()).strip()
                        address_lines = [line.strip() for line in address_text.split('\n') if line.strip() and "+ " not in line]
                        address_main = '\n'.join(address_lines)
                    else:
                        address_main = ''

                    # Initialize list for additional locations
                    locations = []

                    # Extract and clean the first location element from addition-location-wrap
                    first_location_element = await container.query_selector('.addition-location-wrap .location')
                    if first_location_element:
                        first_location_text = (await first_location_element.text_content()).strip()
                        if "+ " not in first_location_text:
                            first_location_lines = [line.strip() for line in first_location_text.split('\n') if line.strip()]
                            first_location_text_cleaned = '\n'.join(first_location_lines)
                            locations.append((f'Adviser Location 1', first_location_text_cleaned))

                    # Extract and clean additional location elements from .other-add
                    additional_location_elements = await container.query_selector_all('.addition-location .other-add')
                    for i, location_element in enumerate(additional_location_elements, start=2):  # Start index at 2 for locations after the first
                        location_text = (await location_element.text_content()).strip()
                        if "+ " not in location_text:
                            location_lines = [line.strip() for line in location_text.split('\n') if line.strip()]
                            location_text_cleaned = '\n'.join(location_lines)
                            locations.append((f'Adviser Location {i}', location_text_cleaned))

                    # Prepare data dictionary
                    data = {
                        "Profile Image": profile_image,
                        "Adviser Name": adviser_name,
                        "Adviser Organization": adviser_org,
                        "Phone Number": phone_numbers,
                        "Adviser Email": adviser_email,
                        "Adviser Website": adviser_website,
                        
                    }

                    # Add each location as separate fields
                    for location_name, location_text in locations:
                        data[location_name] = location_text

                    all_data.append(data)
                except Exception as e:
                    print(f"Error while processing container: {e}")

        page_number = 1
        await scrape_current_page(page_number)

        while True:
            try:
                next_button = await page.query_selector('.pagination__item--next')
                if not next_button:
                    break
                await next_button.click()
                await page.wait_for_timeout(30000)  # Adding explicit wait
                await page.wait_for_selector('.inner-advisors-wrapper', state='visible')
                page_number += 1
                await scrape_current_page(page_number)
            except Exception as e:
                print(f"Pagination ended or encountered an error: {e}")
                break

        seen = set()
        unique_data = []

        for entry in all_data:
            # Normalize the text to avoid case-sensitive duplicates
            adviser_name = entry["Adviser Name"].strip().lower()
            adviser_organization = entry["Adviser Organization"].strip().lower()

            # Create a unique identifier
            identifier = (adviser_name, adviser_organization)
            
            # Add to unique_data if not already seen
            if identifier not in seen:
                seen.add(identifier)
                unique_data.append(entry)

        # Update all_data with unique_data
        all_data = unique_data

        df = pd.DataFrame(unique_data)
        df.to_csv('adviser_info.csv', index=False)

        print(f"Data has been scraped and saved to adviser_info.csv. Total rows fetched: {total_rows_fetched}")
        await browser.close()

url = "https://www.sjp.co.uk/individuals/find-an-adviser"
asyncio.run(scrape_adviser_info(url))
