"""
Government Job Scraper - Combines all 4 sources
Scrapes job listings and saves to jobs.json
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

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
                        'source': 'CareerPower',
                        'title': title,
                        'posts': posts,
                        'qualification': 'N/A',
                        'lastDate': last_date,
                        'link': link
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
                        'source': 'AllGovtJobs',
                        'title': org,
                        'posts': posts_info,
                        'qualification': education,
                        'lastDate': last_date,
                        'link': ''
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
                            'source': 'AllGovtJobs-Filtered',
                            'title': org,
                            'posts': posts_info,
                            'qualification': matched_education,
                            'lastDate': last_date,
                            'link': ''
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
                            'source': 'SarkariResult',
                            'title': title,
                            'posts': num_posts,
                            'qualification': 'N/A',
                            'lastDate': last_date_str,
                            'link': job_link
                        })
                except ValueError:
                    # If date parsing fails, still include it
                    jobs.append({
                        'source': 'SarkariResult',
                        'title': title,
                        'posts': num_posts,
                        'qualification': 'N/A',
                        'lastDate': last_date_str,
                        'link': job_link
                    })
            except Exception as e:
                print(f"  Error parsing job: {e}")
                continue
        
        print(f"Source 4: Found {len(jobs)} jobs")
        return jobs
    
    except Exception as e:
        print(f"Error scraping Source 4: {e}")
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
    
    print(f"\nTotal jobs scraped: {len(all_jobs)}")
    
    if not all_jobs:
        print("No jobs found. Exiting.")
        return
    
    # Add scrape timestamp to each job
    scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for job in all_jobs:
        job['scrapedAt'] = scraped_at
    
    # Create output data structure
    output = {
        'lastUpdated': scraped_at,
        'totalJobs': len(all_jobs),
        'jobs': all_jobs
    }
    
    # Save to JSON file
    print("\nWriting to jobs.json...")
    try:
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print("✅ Successfully saved to jobs.json!")
        
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")


if __name__ == "__main__":
    main()
