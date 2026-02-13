from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

# Initialize the driver
driver = webdriver.Chrome()

# Navigate to the page
driver.get('http://192.168.137.201/rj/basic1.php')

# 1. Set Protocol to "new"
protocol_dropdown = Select(driver.find_element(By.ID, "ProtocolSel"))
protocol_dropdown.select_by_visible_text("new")  # Selects the "new" option
time.sleep(0.5)  # Small delay for JavaScript to update

# 2. Change Run Title to "Artemio Test"
title_field = driver.find_element(By.ID, "Title")
title_field.clear()
title_field.send_keys("Artemio Test")

# 3. Click the START button
start_button = driver.find_element(By.ID, "startButton")
start_button.click()
print("Test started successfully!")
time.sleep(10)

stop_button = driver.find_element(By.ID, "stopButton")
stop_button.click()
print("Test stopped successfully")

# Keep the browser open to see what happens
# driver.quit()  # Uncomment when you want to close