from flask import Flask, render_template, request
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

app = Flask(__name__)

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(options=options)
    return driver


def get_new_link_from_redirect(redirect_url):
    driver = create_driver()
    try:
        driver.get(redirect_url)
        new_link = driver.current_url
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
    return new_link


def get_video_link(show_name):
    driver = create_driver()
    try:
        link = f"https://cinemathek.net/filme/{show_name}"
        driver.get(link)
        try:
            iframe_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.metaframe'))
            )
            src_url = iframe_element.get_attribute('src')
        except TimeoutException:
            print("Das iframe-Element konnte nicht innerhalb von 20 Sekunden gefunden werden.")
            src_url = None
    finally:
        driver.quit()
    return src_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    text_input = request.form['textInput'].replace(' ', '')
    show_name = text_input.strip()

    redirect_url = get_video_link(show_name)
    if redirect_url:
        new_url = get_new_link_from_redirect(redirect_url)
        return new_url
    else:
        return "Video link not found", 404

if __name__ == '__main__':
    app.run(debug=True)
