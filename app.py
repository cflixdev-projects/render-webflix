from flask import Flask, render_template, request
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

app = Flask(__name__)

# Initialize the WebDriver instance outside of the function
options = Options()
options.add_argument("--headless")
options.add_argument('log-level=3')
driver = webdriver.Chrome(options=options)


def get_video_link(show_name, season, episode):
    try:
        link = f"http://186.2.175.5/serie/stream/{show_name}/staffel-{season}/episode-{episode}"
        driver.get(link)
        element = driver.find_element(By.CSS_SELECTOR,
                                      '#wrapper > div.seriesContentBox > div.container.marginBottom > div:nth-child('
                                      '5) > div.hosterSiteVideo > div.inSiteWebStream > div:nth-child(1) > iframe')
        content_value = element.get_attribute('src')
        return content_value
    except Exception as e:
        print("An error occurred:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    text_input = request.form['textInput'].replace(' ', '')
    show_name, season, episode = text_input.split(',')
    video_link = get_video_link(show_name, season, episode)
    return video_link

if __name__ == '__main__':
    app.run(debug=True)
