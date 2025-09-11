
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import pandas as pd

def get_raw_data(url):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "live-table")))

        while True:
            # Find all current "Show more" links
            show_more_links = driver.find_elements(By.XPATH, "//span[contains(text(), 'Show more matches')]/parent::a")
            if not show_more_links:
                break  # No more links to click

            for link in show_more_links:
                try:
                    # Scroll to the link to ensure it's visible
                    driver.execute_script("arguments[0].scrollIntoView();", link)
                    link.click()
                    # Wait for the link to become stale (content expanded)
                    WebDriverWait(driver, 5).until(EC.staleness_of(link))
                except Exception:
                    pass  # Ignore if already expanded or error

        soup = bs(driver.page_source, 'html.parser')
        return soup
    finally: 
        driver.quit()


def get_epl_fixtures(first_year, second_year):
    soup = get_raw_data(f'https://www.livesport.com/uk/football/england/premier-league-{first_year}-{second_year}/results/')
    fixtures = soup.find('div', class_='sportName soccer')
    all_div = []
    for div in fixtures.find_all('div', recursive=False):
        classes = div.get('class')
        if not 'event__match' in classes:
            continue
        all_div.append(div)

    season = []
    
    for match in all_div:
        home_team = match.find('div', class_='wcl-participant_bctDY event__homeParticipant').text
        away_team = match.find('div', class_='wcl-participant_bctDY event__awayParticipant').text
        date_el = match.find('div', class_='event__time')
        date = date_el.get_text()
        home_score = match.find('span', class_='wcl-matchRowScore_fWR-Z wcl-isFinal_7U4ca event__score event__score--home').text
        away_score = match.find('span', class_='wcl-matchRowScore_fWR-Z wcl-isFinal_7U4ca event__score event__score--away').text


        day_month = date.split()[0].replace('.', '')
        time_part = date.split()[1]

        day = int(day_month[:2])
        month = int(day_month[2:])
        year = first_year if month >= 8 else second_year

        match_day = f"{year}-{month:02d}-{day:02d}"

        season.append({
            'home_team': home_team,
            'away_team': away_team,
            'match_day': match_day,
            'time': time_part,
            'home_score': home_score,
            'away_score': away_score
        })

    return pd.DataFrame(season)
