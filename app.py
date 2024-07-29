from flask import Flask, render_template, request
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

app = Flask(__name__)

# Initialize the WebDriver instance outside of the Flask application context
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('log-level=3')
driver = webdriver.Chrome(options=options)


def get_new_link_from_redirect(driver, redirect_url):
    driver.get(redirect_url)
    new_link = driver.current_url
    print('aktueller neuere link ' + new_link)
    return new_link


def get_video_link(driver, show_name, season=None, episode=None):
    if season and episode:
        link = f"http://186.2.175.5/serie/stream/{show_name}/staffel-{season}/episode-{episode}"
    else:
        link = f"https://cinemathek.net/filme/{show_name}"

    driver.get(link)

    if season and episode:
        element = driver.find_element(By.CSS_SELECTOR,
                                      '#wrapper > div.seriesContentBox > div.container.marginBottom > div:nth-child('
                                      '5) > div.hosterSiteVideo > div.inSiteWebStream > div:nth-child(1) > iframe')
        content_value = element.get_attribute('src')
    else:
        try:
            iframe_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.metaframe'))
            )
            content_value = iframe_element.get_attribute('src')
        except TimeoutException:
            print("Das iframe-Element konnte nicht innerhalb von 20 Sekunden gefunden werden.")
            content_value = None

    print('content_value = ' + content_value)
    return content_value


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    text_input = request.form['textInput'].replace(' ', '')
    inputs = text_input.split(',')

    if len(inputs) == 3:
        show_name, season, episode = inputs
        redirect_url = get_video_link(driver, show_name, season, episode)
    else:
        show_name = inputs[0]
        redirect_url = get_video_link(driver, show_name)

    if redirect_url:
        new_url = get_new_link_from_redirect(driver, redirect_url)
        return new_url
    else:
        return "Video link not found", 404


if __name__ == '__main__':
    app.run(debug=True)
