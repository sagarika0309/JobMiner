# run.py

import pandas as pd
import matplotlib.pyplot as plt
from miners.linkedin_scraper import scrape_linkedin_jobs, save_jobs_to_csv


def ask_user_input():
    print("Welcome to LinkedIn Job Scraper and Analyzer!")
    title = input("Enter job title (e.g., Python Developer): ")
    location = input("Enter location (e.g., Ahmedabad): ")
    num_pages = int(input("Enter number of pages to scrape: "))

    return title, location, num_pages

def preprocess_data(filename):
    try:
        df = pd.read_csv(filename)
        # Perform data cleaning, preprocessing, etc.
        # Example: Remove rows with missing values
        df_cleaned = df.dropna()

        return df_cleaned
    except Exception as e:
        print(f"Error preprocessing data: {e}")
        return None

def analyze_data(df):
    try:
        # Perform data analysis (example: count number of jobs by company)
        job_counts = df['company_name'].value_counts()

        return job_counts
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None

def display_results(job_counts):
    if job_counts is not None:
        print("\n--- Job Counts by Company ---")
        print(job_counts)

        # Plotting bar chart
        plt.figure(figsize=(10, 6))
        job_counts[:10].plot(kind='bar')
        plt.title('Top 10 Companies Hiring')
        plt.xlabel('Company Name')
        plt.ylabel('Number of Jobs')
        plt.xticks(rotation=45, ha='right') 
        plt.tight_layout()
        plt.show()
    else:
        print("No results to display. Check previous steps.")

if __name__ == "__main__":
    title, location, num_pages = ask_user_input()

    job_list = scrape_linkedin_jobs(title, location, 0, num_pages)
    if job_list:
        save_jobs_to_csv(job_list, 'treasure_chest/raw_gems/linkedin_jobs.csv')

        processed_data = preprocess_data('treasure_chest/raw_gems/linkedin_jobs.csv')
        if processed_data is not None:
            analysis_results = analyze_data(processed_data)
            display_results(analysis_results)
    else:
        print("No job data retrieved. Check your request or try again later.")
