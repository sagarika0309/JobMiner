import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def fetch_html(url, headers):
    try:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        response = session.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching HTML from {url}: {e}")
        return None

def extract_job_ids(html):
    job_ids = []
    if html:
        soup = BeautifulSoup(html, "html.parser")
        page_jobs = soup.find_all('li')

        for job in page_jobs:
            base_card_div = job.find('div', {"class": "base-card"})
            if base_card_div:
                job_id = base_card_div.get("data-entity-urn").split(":")[3]
                job_ids.append(job_id)

    return job_ids

def extract_job_details(job_id, headers):
    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        response = session.get(job_url, headers=headers)
        response.raise_for_status()

        job_soup = BeautifulSoup(response.text, "html.parser")
        
        job_post = {
            "job_title": job_soup.find("h2", {"class": "top-card-layout__title"}).text.strip() if job_soup.find("h2", {"class": "top-card-layout__title"}) else None,
            "company_name": job_soup.find("a", {"class": "topcard__org-name-link"}).text.strip() if job_soup.find("a", {"class": "topcard__org-name-link"}) else None,
            "time_posted": job_soup.find("span", {"class": "posted-time-ago__text"}).text.strip() if job_soup.find("span", {"class": "posted-time-ago__text"}) else None,
            "num_applicants": job_soup.find("span", {"class": "num-applicants__caption"}).text.strip() if job_soup.find("span", {"class": "num-applicants__caption"}) else None
        }

        return job_post
    except requests.RequestException as e:
        print(f"Error extracting job details for job ID {job_id}: {e}")
        return None

def scrape_linkedin_jobs(title, location, start, num_pages):
    base_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.linkedin.com/',
        'Connection': 'keep-alive',
    }
    job_list = []

    for page in range(num_pages):
        try:
            html_content = fetch_html(base_url, headers)
            if not html_content:
                continue

            job_ids = extract_job_ids(html_content)

            for job_id in job_ids:
                job_details = extract_job_details(job_id, headers)
                if job_details:
                    job_list.append(job_details)

                time.sleep(random.uniform(1, 3))  # Random delay between requests

            start += 25
            base_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"

        except Exception as e:
            print(f"Error scraping LinkedIn jobs on page {page}: {e}")

    return job_list

def save_jobs_to_csv(job_list, filename):
    try:
        jobs_df = pd.DataFrame(job_list)
        jobs_df.to_csv(filename, index=False)
        print(f"Job data saved to {filename}. Total jobs: {len(job_list)}")
    except Exception as e:
        print(f"Error saving job data to CSV: {e}")

if __name__ == "__main__":
    title = 'Python Developer'
    location = 'Ahmedabad'
    start = 0
    num_pages = 4

    job_list = scrape_linkedin_jobs(title, location, start, num_pages)

    if job_list:
        save_jobs_to_csv(job_list, 'treasure_chest/raw_gems/linkedin_jobs.csv')
    else:
        print("No job data retrieved. Check your request or try again later.")

      



        
            
                
            
    