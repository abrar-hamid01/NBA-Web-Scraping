from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_nba_stats(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', id='per_game')
    
    if not table:
        print("No table found on the page")
        return None

    headers_row = table.find('thead').find('tr')
    headers = [th.text.strip() for th in headers_row.find_all('th')]

    try:
        player_name_index = headers.index('Player')
        points_index = headers.index('PTS')
        rebounds_index = headers.index('TRB')
        assists_index = headers.index('AST')
    except ValueError as e:
        print(f"Expected column header not found: {e}")
        return None

    rows = table.find('tbody').find_all('tr')
    player_stats = []
    
    for row in rows:
        cells = row.find_all(['th', 'td'])
        player_name = cells[player_name_index].text.strip()
        points = cells[points_index].text.strip()
        rebounds = cells[rebounds_index].text.strip()
        assists = cells[assists_index].text.strip()
        
        player_stats.append({
            'Player': player_name,
            'Points': points,
            'Rebounds': rebounds,
            'Assists': assists
        })
    
    return player_stats

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '')
        if url:
            player_stats = scrape_nba_stats(url)
            if player_stats:
                return render_template('stats.html', player_stats=player_stats)
            else:
                return render_template('index.html', error="Failed to retrieve or parse data from the URL.")
        else:
            return render_template('index.html', error="Please provide a valid URL.")
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
