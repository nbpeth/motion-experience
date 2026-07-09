from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path 

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

svc = webdriver.ChromeService(executable_path=binary_path)
driver = webdriver.Chrome(service=svc, options=options)

driver.get("http://localhost:8000")
driver.maximize_window()
