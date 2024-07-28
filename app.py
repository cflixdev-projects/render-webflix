import logging
from flask import Flask, render_template, request, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Initialize the WebDriver instance outside of the Flask application context
options = Options()
options.add_argument("--headless")
options.add_argument('log-level=3')

try:
    driver = webdriver.Chrome(options=options)
    logging.debug('WebDriver initialized successfully')
except Exception as e:
    logging.error('Error initializing WebDriver: %s', e)
    driver = None

def get_new_link_from_redirect(driver, redirect_url):
    try:
        driver.get(redirect_url)
        new_link = driver.current_url
        logging.debug('New redirect link: %s', new_link)
        return new_link
    except Exception as e:
        logging.error('Error getting new link from redirect: %s', e)
        return None

def get_video_link(driver, show_name, season, episode):
    try:
        link = f"http://186.2.175.5/serie/stream/{show_name}/staffel-{season}/episode-{episode}"
        driver.get(link)
        element = driver.find_element(By.CSS_SELECTOR,
                                      '#wrapper > div.seriesContentBox > div.container.marginBottom > div:nth-child('
                                      '5) > div.hosterSiteVideo > div.inSiteWebStream > div:nth-child(1) > iframe')
        content_value = element.get_attribute('src')
        logging.debug('Content value: %s', content_value)
        return content_value
    except Exception as e:
        logging.error('Error getting video link: %s', e)
        return None

def get_movie_link(driver, show_name):
    try:
        link = f"https://cinemathek.net/filme/{show_name}"
        driver.get(link)
        iframe_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.metaframe'))
        )
        src_url = iframe_element.get_attribute('src')
        logging.debug('Src URL of the iframe: %s', src_url)
        return src_url
    except Exception as e:
        logging.error('Error getting movie link: %s', e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        switch_value = request.form['switchValue']
        text_input = request.form['textInput'].replace(' ', '')

        if switch_value == 'Shows':
            show_name, season, episode = text_input.split(',')
            redirect_url = get_video_link(driver, show_name, season, episode)
        elif switch_value == 'Movies':
            show_name = text_input.strip()
            logging.debug('Show name: %s', show_name)
            redirect_url = get_movie_link(driver, show_name)
        else:
            return jsonify({"error": "Invalid switch value"}), 400

        if redirect_url:
            new_url = get_new_link_from_redirect(driver, redirect_url)
            if new_url:
                return new_url
            else:
                return jsonify({"error": "Failed to retrieve new URL from redirect"}), 500
        else:
            return jsonify({"error": "Failed to retrieve redirect URL"}), 500
    except Exception as e:
        logging.error('Error in search route: %s', e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run()
