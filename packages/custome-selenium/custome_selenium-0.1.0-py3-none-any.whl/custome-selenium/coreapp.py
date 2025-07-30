from typing import Literal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
def wait_element(
    driver: WebDriver,
    type_element: Literal["xpath", "name", "id", "link_text", "partial_link_text", "css", "class", "tag"] = "xpath",
    element: str= "",
    time_out: int = 10) -> bool:
    by_mapping = {
        "xpath": By.XPATH,
        "name": By.NAME,
        "id": By.ID,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME
    }

    by_type = by_mapping.get(type_element)
    if not by_type:
        print(f"Unsupported type_element: {type_element}")
        return False

    try:
        return WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((by_type, element))
        )
    except Exception as e:
        print(f"Không tìm thấy phần tử với {type_element}: {element}")
        print("Lỗi:", e)
        return False
def wait_all_elements(
    driver,
    type_element: Literal["xpath", "name", "id", "link_text", "partial_link_text", "css", "class", "tag"] = "xpath",
    element: str= "",
    time_out: int = 10) -> bool:
    by_mapping = {
        "xpath": By.XPATH,
        "name": By.NAME,
        "id": By.ID,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME
    }

    by_type = by_mapping.get(type_element)
    if not by_type:
        print(f"Unsupported type_element: {type_element}")
        return False
    try:
        return WebDriverWait(driver, time_out).until(
            EC.presence_of_all_elements_located((by_type, element))
        )
    except Exception as e:
        print(f"Không tìm thấy phần tử với {type_element}: {element}")
        print("Lỗi:", e)
        return False
def scroll_top_bottom_page(driver: WebDriver, type_scroll: Literal["top", "bottom"] = "bottom"):
    if type_scroll == "bottom":
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    elif type_scroll == "top":
        driver.execute_script("window.scrollTo(0, 0);")
    else:
        print(f"[!] type_scroll không hợp lệ: {type_scroll}")
def scroll_custom_up_down_page_with_distance(driver: WebDriver, direction: Literal["up", "down"] = "down", distance: int = 300):
    if direction == "down":
        driver.execute_script(f"window.scrollBy(0, {distance});")
    elif direction == "up":
        driver.execute_script(f"window.scrollBy(0, -{distance});")
    else:
        print(f"[!] direction không hợp lệ: {direction}")