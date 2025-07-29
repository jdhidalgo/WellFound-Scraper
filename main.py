import requests, datetime, re
from bs4 import BeautifulSoup

WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1399602828804100136/3m1DjL5zsNLu0eSHyr5I_fIMxWVNMiyeslK2zKLDDF3JwOPNoJI9pUhSJESElk8iiKS5"

def fetch_wellfound():
    # Normally: requests.get("https://wellfound.com/jobs") — simulate for now
    html = """
    <html><body><div class="jobs-listing">
        <div class="job-posting">
            <a href="https://wellfound.com/jobs/999-entry-data-clerk">Entry-Level Data Clerk</a>
            <div class="company-name">RocketTech</div>
            <div class="job-description">Looking for a motivated individual for fully remote data entry. No degree or prior experience needed.</div>
            <div class="post-date">Posted 5 days ago</div>
        </div>
    </div></body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for job in soup.select(".job-posting"):
        title = job.select_one("a").text.strip()
        url = job.select_one("a")["href"]
        company = job.select_one(".company-name").text.strip()
        desc = job.select_one(".job-description").text.lower()
        post_date_text = job.select_one(".post-date").text.strip()

        if any(x in company.lower() for x in ["emergent", "bae", "goldbelt", "crowdstrike"]):
            continue
        if not ("no experience" in desc or "entry-level" in title.lower()):
            continue

        days_ago = int(re.search(r"(\d+)", post_date_text).group(1))
        if days_ago > 15:
            continue

        jobs.append({
            "title": title,
            "company": company,
            "url": url,
            "date": (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        })
    return jobs

def send_to_discord(jobs):
    for job in jobs:
        data = {
            "username": "Remote Job Bot",
            "embeds": [{
                "title": "📌 New Remote Job Found!",
                "color": 5814783,
                "fields": [
                    {"name": "Company", "value": job["company"]},
                    {"name": "Title", "value": job["title"]},
                    {"name": "Apply Link", "value": f"[Click here]({job['url']})"}
                ],
                "footer": {"text": f"Posted {job['date']}"}
            }]
        }
        requests.post(WEBHOOK_URL, json=data)

if __name__ == "__main__":
    new_jobs = fetch_wellfound()
    if new_jobs:
        send_to_discord(new_jobs)
