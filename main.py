import os
from dotenv import load_dotenv # type: ignore
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from sendgrid import SendGridAPIClient # type: ignore
from sendgrid.helpers.mail import Mail # type: ignore
import tldextract # type: ignore
import re

load_dotenv()

def get_domain(url):
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"

def get_company_logo(domain_name):
    logo_url = f"https://logo.clearbit.com/{domain_name}"

    response = requests.get(logo_url)

    if response.status_code == 200:
        return logo_url
    else:
        return "no_logo_found"

google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
cse_id = os.getenv("CSE_ID")
sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL")


query = 'Software Engineer "United States" site:greenhouse.io'
experience = ["New grad", "Entry Level", "Junior"]
roles = ["Software Engineer", "Software Development Engineer", "Backend Engineer", "Backend Developer", "Full Stack Developer"]
keywords = ["entry level", "junior", "level I", "software engineer"]
# skills = []

jobData = []
for start in range(1, 101, 10): 
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_search_api_key}&cx={cse_id}&start={start}"
    response = requests.get(url)
    # print(response)
    data = response.json()
    # print(data)
    # print("\n")
    
    if 'items' in data:
        jobData.extend(data['items'])
    else:
        break


filteredJobs = []

for data in jobData:
    try:
        response = requests.get(data['link'], headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text if soup.find("title") else "N/A"

        meta_tags = {meta.get("property", ""): meta.get("content", "") for meta in soup.find_all("meta")}
        print(meta_tags)

        url = meta_tags['og:url']

        print(url)

        domain = get_domain(url)

        # if domain == "lever.co":

        
        company_logo = get_company_logo(domain)

        page_text = soup.get_text(separator=" ").lower()

        if any(re.search(rf"\b{k.lower()}\b", page_text) for k in keywords):
            print("adding job")
            filteredJobs.append({"title": title, "url": data['link'], "logo": company_logo})
            # filteredJobs.append({"title": title, "url": data['link']})

    except Exception as e:
        print(f"Error processing {url}: {e}")

with open("filtered_jobs.txt", "w") as f:
    for job in filteredJobs:
        f.write(job['title'] + "\n" + job['url'] + "\n" + job['logo'] + "\n\n")


def sendEmail():
    content = ""

    with open("filtered_jobs.txt", "r") as f:
        content = f.read() 
        print(content) 

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='Trial',
        html_content=content)
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
