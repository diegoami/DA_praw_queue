import asyncio
import praw
import threading
import yaml

MAX_SUBMITTED=1000

lock = asyncio.Lock()
submitted = []

def print_submission(subr_name, submission):
    global submitted
    print(subr_name)
    print(submission.title)
    print(submission.url)
    if (submission.url not in submitted):
        submitted.append(submission.url)
        if (len(submitted) > MAX_SUBMITTED):
            submitted = submitted[-MAX_SUBMITTED:]

async def print_submissions(reddit, subreddit_name, top=25):
    print("STARTING THREAD "+subreddit_name)
    for submission in reddit.subreddit(subreddit_name).stream.submissions():
        print_submission(subreddit_name, submission)

async def submission_loop(reddit, subreddit_names):
    for subreddit_name in subreddit_names:
        await print_submissions(reddit, subreddit_name)

if __name__ == "__main__":
    auth_config_file = 'auth.yml'
    scrape_config_file = 'scrape.yml'
    with open(auth_config_file) as f:
        auth_config = yaml.safe_load(f)
    with open(scrape_config_file) as f:
        scrape_config = yaml.safe_load(f)
    reddit = praw.Reddit(**auth_config["reddit_config"])
    subreddit_names = scrape_config['subreddits']

    asyncio.run(submission_loop(reddit, subreddit_names))

