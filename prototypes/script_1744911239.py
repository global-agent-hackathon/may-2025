To create a Python script that scrapes the titles and ratings of the top 10 movies from IMDb and then saves this data into a CSV file, you can use libraries such as `requests` for fetching the webpage, `BeautifulSoup` for parsing HTML, and `pandas` for organizing the data and saving it to CSV. Here's a complete script which accomplishes the task:

### Python Script

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_imdb_top_10():
    # URL of IMDb top movie chart
    url = 'https://www.imdb.com/chart/top/'
    
    # Headers to mimic a browser visit
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Fetch the page
    response = requests.get(url, headers=headers)
    
    # If the request was successful, proceed
    if response.status_code == 200:
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all the tr elements in the tbody of the table with class chart full-width
        movies_table = soup.find('tbody', class_='lister-list').find_all('tr')[:10]  # Only top 10
        
        # List to hold movie data
        movies_list = []
        
        # Extract title and rating of each movie
        for movie in movies_table:
            title = movie.find('td', class_='titleColumn').a.text
            rating = movie.find('td', class_='ratingColumn imdbRating').strong.text
            movies_list.append({'Title': title, 'Rating': rating})
        
        return movies_list
    
    else:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")
        return []

def save_to_csv(movies_list):
    # Convert list to DataFrame
    df = pd.DataFrame(movies_list)
    
    # Save DataFrame to CSV
    df.to_csv('imdb_top_10_movies.csv', index=False)
    print("Saved to 'imdb_top_10_movies.csv'")

def main():
    print("Fetching IMDb's Top 10 Movies...")
    top_10_movies = fetch_imdb_top_10()
    if top_10_movies:
        save_to_csv(top_10_movies)

if __name__ == "__main__":
    main()
```

### Requirements

Before running the script, ensure you have the necessary Python packages installed. You can install them using pip:

```sh
pip install requests beautifulsoup4 pandas
```

### How to Run

1. Save the script in a file named `imdb_scraper.py`.
2. Open your terminal or command prompt.
3. Navigate to the directory where the script is saved.
4. Run the script by typing `python imdb_scraper.py`.

The script will fetch the top 10 movies from IMDb and save them to a CSV file named `imdb_top_10_movies.csv` in the same directory where the script is located. Make sure you have internet access and the IMDb website does not change its layout for the script to work correctly.