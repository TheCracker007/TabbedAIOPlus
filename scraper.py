"""
Government Job Scraper - Combines all 4 sources
Scrapes job listings and writes to Google Sheets
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
          'https://www.googleapis.com/auth/drive']

def get_google_sheet():
    """Authenticate and get Google Sheet"""
    # Load credentials from environment variable (set in GitHub Secrets)
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not set")
    
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # Open the sheet (you'll need to create this and share it with the service account)
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID environment variable not set")
    
    return client.open_by_key(sheet_id)


def scrape_source1():
    """Source 1: careerpower.in - WITHOUT ScrapingAnt (direct scraping)"""
    print("Scraping Source 1: careerpower.in")
    
    try:
        url = "https://www.careerpower.in/government-jobs.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = []
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    recruitment_name = cols[0].get_text(strip=True)
                    last_date = cols[2].get_text(strip=True)
                    
                    link_tag = cols[0].find("a")
                    link = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""
                    
                    # Split recruitment name into title and posts
                    if ' for ' in recruitment_name:
                        title, posts = recruitment_name.split(' for ', 1)
                    else:
                        title = recruitment_name
                        posts = "N/A"
                    
                    data.append({
                        'Source': 'CareerPower',
                        'Title': title,
                        'Posts': posts,
                        'Qualification': 'N/A',
                        'Last Date': last_date,
                        'Link': link
                    })
        
        print(f"Source 1: Found {len(data)} jobs")
        return data
    
    except Exception as e:
        print(f"Error scraping Source 1: {e}")
        return []


def scrape_source2():
    """Source 2: allgovernmentjobs.in - All jobs sorted by date"""
    print("Scraping Source 2: allgovernmentjobs.in (all jobs)")
    
    try:
        base_url = "https://allgovernmentjobs.in/latest-government-jobs"
        num_pages = 25
        all_data = []
        
        for page in range(1, num_pages + 1):
            url = f"{base_url}/page/{page}" if page > 1 else base_url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
            
            table_rows = soup.select(".table-bordered tbody tr")
            
            for row in table_rows:
                columns = row.find_all("td")
                if len(columns) >= 4:
                    org = columns[0].text.strip()
                    job_details = columns[1].text.strip()
                    education = columns[2].text.strip()
                    last_date = columns[3].text.strip()
                    
                    # Extract posts info
                    posts_info = job_details.split('-')[-1].strip() if '-' in job_details else job_details
                    
                    all_data.append({
                        'Source': 'AllGovtJobs',
                        'Title': org,
                        'Posts': posts_info,
                        'Qualification': education,
                        'Last Date': last_date,
                        'Link': ''
                    })
            
            print(f"  Scraped page {page}/{num_pages}")
        
        print(f"Source 2: Found {len(all_data)} jobs")
        return all_data
    
    except Exception as e:
        print(f"Error scraping Source 2: {e}")
        return []


def scrape_source3():
    """Source 3: allgovernmentjobs.in - Filtered by education level"""
    print("Scraping Source 3: allgovernmentjobs.in (filtered)")
    
    # This is similar to source 2 but with education filter
    # For simplicity, we'll mark these with a different source name
    try:
        base_url = "https://allgovernmentjobs.in/latest-government-jobs"
        num_pages = 25
        education_levels = ["B.E/ B.Tech", "Any Degree", "Electronics and Communication Engineering", 
                          "10th", "12th", "Intermediate (10+2)"]
        all_data = []
        
        for page in range(1, num_pages + 1):
            url = f"{base_url}/page/{page}" if page > 1 else base_url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
            
            table_rows = soup.select(".table-bordered tbody tr")
            
            for row in table_rows:
                columns = row.find_all("td")
                if len(columns) >= 4:
                    org = columns[0].text.strip()
                    job_details = columns[1].text.strip()
                    education = columns[2].text.strip()
                    last_date = columns[3].text.strip()
                    
                    # Filter by education level
                    matched_education = None
                    for el in education_levels:
                        if el in education:
                            matched_education = el
                            break
                    
                    if matched_education:
                        posts_info = job_details.split('-')[-1].strip() if '-' in job_details else job_details
                        
                        all_data.append({
                            'Source': 'AllGovtJobs-Filtered',
                            'Title': org,
                            'Posts': posts_info,
                            'Qualification': matched_education,
                            'Last Date': last_date,
                            'Link': ''
                        })
            
            print(f"  Scraped page {page}/{num_pages}")
        
        print(f"Source 3: Found {len(all_data)} jobs")
        return all_data
    
    except Exception as e:
        print(f"Error scraping Source 3: {e}")
        return []


def scrape_source4():
    """Source 4: sarkariresult.app - Latest notifications"""
    print("Scraping Source 4: sarkariresult.app")
    
    try:
        url = 'https://www.sarkariresult.app/latest-jobs/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        
        for element in soup.select('ul.su-posts li.su-post')[2:]:
            try:
                job_title = element.a.get_text(strip=True)
                job_details = element.span.get_text(strip=True) if element.span else ''
                job_link = element.a['href'] if element.a else ''
                
                # Split title
                split_title = job_title.rsplit(' ', 2)
                title = ' '.join(split_title[:-2]) if len(split_title) > 2 else job_title
                num_posts = ' '.join(split_title[-2:]) if len(split_title) > 2 else ''
                
                # Extract last date
                last_date_str = job_details.replace('Last Date:', '').replace('(', '').replace(')', '').strip()
                
                try:
                    last_date = datetime.strptime(last_date_str, '%d %B %Y').date()
                    # Only include if date is today, yesterday, or future
                    if last_date >= (datetime.now() - timedelta(days=1)).date():
                        jobs.append({
                            'Source': 'SarkariResult',
                            'Title': title,
                            'Posts': num_posts,
                            'Qualification': 'N/A',
                            'Last Date': last_date_str,
                            'Link': job_link
                        })
                except ValueError:
                    # If date parsing fails, still include it
                    jobs.append({
                        'Source': 'SarkariResult',
                        'Title': title,
                        'Posts': num_posts,
                        'Qualification': 'N/A',
                        'Last Date': last_date_str,
                        'Link': job_link
                    })
            except Exception as e:
                print(f"  Error parsing job: {e}")
                continue
        
        print(f"Source 4: Found {len(jobs)} jobs")
        return jobs
    
    except Exception as e:
        print(f"Error scraping Source 4: {e}")
        return []


def scrape_source5():
    """Source 5: PLACEHOLDER for future website"""
    print("Source 5: Not configured yet (placeholder)")
    return []


def main():
    """Main scraping function"""
    print("=" * 50)
    print("Starting Job Scraper")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    # Scrape all sources
    all_jobs = []
    all_jobs.extend(scrape_source1())
    all_jobs.extend(scrape_source2())
    all_jobs.extend(scrape_source3())
    all_jobs.extend(scrape_source4())
    all_jobs.extend(scrape_source5())
    
    print(f"\nTotal jobs scraped: {len(all_jobs)}")
    
    if not all_jobs:
        print("No jobs found. Exiting.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_jobs)
    
    # Add scrape timestamp
    df['Scraped At'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns
    df = df[['Source', 'Title', 'Posts', 'Qualification', 'Last Date', 'Link', 'Scraped At']]
    
    print("\nWriting to Google Sheets...")
    try:
        sheet = get_google_sheet()
        worksheet = sheet.worksheet('Jobs')  # Make sure this sheet exists
        
        # Clear existing data
        worksheet.clear()
        
        # Write headers and data
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        print("✅ Successfully updated Google Sheet!")
        
    except Exception as e:
        print(f"❌ Error updating Google Sheet: {e}")
        # Save to local CSV as backup
        df.to_csv('jobs_backup.csv', index=False)
        print("💾 Saved backup to jobs_backup.csv")


if __name__ == "__main__":
    main()
