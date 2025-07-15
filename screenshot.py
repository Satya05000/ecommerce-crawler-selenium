# screenshot.py
import os
import datetime

def save_screenshot(driver, name, folder="screenshots"):
    """
    Captures a screenshot from the driver and saves it to the specified folder with a timestamped name.
    
    Args:
        driver: Selenium WebDriver instance.
        name (str): Name to include in the screenshot filename.
        folder (str): Folder to save the screenshot in. Default is 'screenshots'.
    """
    try:
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f"{name}_{timestamp}.png")
        driver.save_screenshot(path)
        print(f"Screenshot saved: {path}")
    except Exception as e:
        print(f"Failed to save screenshot '{name}': {e}")
