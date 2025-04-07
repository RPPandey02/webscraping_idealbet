from selenium import webdriver

options = webdriver.FirefoxOptions()
# Set your desired options here

# Specify the timeout value (e.g., 10 seconds) for the connect operation
connect_timeout = 10

# Create the WebDriver instance with the specified timeout
driver = webdriver.Firefox(executable_path='./geckodriver', options=options, timeout=connect_timeout)
