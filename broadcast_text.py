import time
import sys
import unicodedata
import emoji
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure Chrome options
chrome_profile_path = r"D:/timothysubroto/IT Stuffs/broadcast/chrome-whatsapp-profile"

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_path}")  # Keep login session
options.add_argument("--remote-debugging-port=9222")  # Prevents multiple instances

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)  # Set up a wait for elements

# Countdown timer for WhatsApp Web initialization
driver.get(f"https://web.whatsapp.com/")
wait_time = 20  # Adjust the wait time as needed
for remaining in range(wait_time, 0, -1):
    sys.stdout.write(f"\r⏳ Waiting for WhatsApp Web to initialize... {remaining} sec")
    sys.stdout.flush()
    time.sleep(1)
print("\n✅ WhatsApp Web should be ready!")
print("\nStarting send sequence... \n")

# Function to remove unsupported characters but keep emojis
def normalize_message(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] not in ['C', 'Z'] or emoji.is_emoji(c))

# Function to send message
def send_whatsapp_message(phone_number, message):
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")

def send_whatsapp_message(phone_number, message):
    """Sends a multi-line text message to a WhatsApp number and waits for confirmation."""
    try:
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")

        # ✅ Wait a few seconds for the page to load
        time.sleep(3)

        # ✅ Check if the invalid number popup appears
        try:
            invalid_number_popup = WebDriverWait(driver, 7).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Phone number shared via url is invalid')]"))
            )
            if invalid_number_popup:
                print(f"❌ Invalid number: {phone_number} - Number does not exist on WhatsApp.")

                # ✅ Try to close the popup
                try:
                    ok_button = driver.find_element(By.XPATH, "//div[@role='button' and text()='OK']")
                    ok_button.click()  # Click the OK button to close the popup
                    time.sleep(1)  # Small delay to ensure it's closed
                except NoSuchElementException:
                    pass  # If "OK" button is not found, continue

                return  # Skip this number and move to the next one

        except TimeoutException:
            pass  # ✅ No invalid number popup detected, continue normally

        # ✅ Extra check: Sometimes WhatsApp shows the error in a different way
        error_message = driver.find_elements(By.XPATH, "//div[contains(text(), 'We couldn’t find a WhatsApp account for this number')]")
        if error_message:
            print(f"❌ Invalid number: {phone_number} - No WhatsApp account found.")
            return  # Skip this number

        # ✅ Wait for chat to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Type a message']")))

        # ✅ Type the message while preserving line breaks
        message_input = driver.find_element(By.XPATH, "//div[@aria-label='Type a message']")
        for line in message.split("\n"):
            message_input.send_keys(line)
            message_input.send_keys(Keys.SHIFT + Keys.ENTER)  # Add a new line
        message_input.send_keys(Keys.ENTER)  # Send the message

        # ✅ Wait for the clock icon (pending status) to disappear
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.XPATH, "//span[@data-icon='msg-time']"))
        )

        print(f"✅ Message successfully sent to {phone_number}")

    except (NoSuchElementException, TimeoutException):
        print(f"❌ Failed to send message to {phone_number}: WhatsApp UI elements not found.")

    except WebDriverException as e:
        print(f"❌ Failed to send message to {phone_number}: WebDriver error - {e}")

    except Exception as e:
        print(f"❌ Unexpected error while sending message to {phone_number}: {e}")

    # Wait for chat to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Type a message']")))

    # Type the message while preserving line breaks
    message_input = driver.find_element(By.XPATH, "//div[@aria-label='Type a message']")
    for line in message.split("\n"):  # Split message by lines
        message_input.send_keys(line)
        message_input.send_keys(Keys.SHIFT + Keys.ENTER)  # Add a new line
    message_input.send_keys(Keys.ENTER)  # Finally, send the message

    # Wait for the clock icon (pending status) to disappear
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.XPATH, "//span[@data-icon='msg-time']"))
    )

# Read numbers from a text file
with open("D:/timothysubroto/IT Stuffs/broadcast/numbers.txt", "r") as file:
    phone_numbers = [line.strip() for line in file.readlines()]

# Read message from a text file
with open("D:/timothysubroto/IT Stuffs/broadcast/message.txt", "r", encoding="utf-8") as file:
    message_text = file.read().strip()  # Read the whole message & remove extra spaces

# Send the message to each number
for number in phone_numbers:
    try:
        send_whatsapp_message(number, message_text)
    except Exception as e:
        print(f"❌ Failed to send message to {number}: {e}")

# Keep the browser open for manual verification
print("✅ Done. Keeping browser open.")
input("Press Enter to close the browser...")
driver.quit()
