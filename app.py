from flask import Flask, render_template, request, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Initialize logging

# Initialize the WebDriver instance outside of the Flask application context
options = Options()
options.add_argument("--headless")
options.add_argument('log-level=3')

try:
    driver = webdriver.Chrome(options=options)
except Exception as e:
    driver = None

def get_new_link_from_redirect(driver, redirect_url):
    try:
        driver.get(redirect_url)
        new_link = driver.current_url
        return new_link
    except Exception as e:
        return None

def get_video_link(driver, show_name, season, episode):
    try:
        link = f"http://186.2.175.5/serie/stream/{show_name}/staffel-{season}/episode-{episode}"
        driver.get(link)
        element = driver.find_element(By.CSS_SELECTOR,
                                      '#wrapper > div.seriesContentBox > div.container.marginBottom > div:nth-child('
                                      '5) > div.hosterSiteVideo > div.inSiteWebStream > div:nth-child(1) > iframe')
        content_value = element.get_attribute('src')
        return content_value
    except Exception as e:
        return None

def get_movie_link(driver, show_name):
    try:
        link = f"https://cinemathek.net/filme/{show_name}"
        driver.get(link)
        iframe_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.metaframe'))
        )
        src_url = iframe_element.get_attribute('src')
        return src_url
    except Exception as e:
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
            try:
                show_name, season, episode = text_input.split(',')
                redirect_url = get_video_link(driver, show_name, season, episode)
            except ValueError:
                return jsonify({"error": "Invalid input format for shows. Expected format: show_name,season,episode"}), 400
        elif switch_value == 'Movies':
            show_name = text_input.strip()
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
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)

