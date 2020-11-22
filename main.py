import yaml
import praw
import threading
MAX_SUBMITTED=1000

lock = threading.Lock()
submitted = []


def print_submissions(reddit, subreddit_name, top=25):
    print("STARTING THREAD "+subreddit_name)
    for submission in reddit.subreddit(subreddit_name).stream.submissions():
        lock.acquire()
        if (submission.url not in submitted):
            print(subreddit_name)
            print(submission.title)
            print(submission.url)
            submitted.append(submission.url)
            if (len(submitted) > MAX_SUBMITTED):
                submitted = submitted[-MAX_SUBMITTED:]
        lock.release()

if __name__ == "__main__":
    auth_config_file = 'auth.yml'
    scrape_config_file = 'scrape.yml'
    with open(auth_config_file) as f:
        auth_config = yaml.safe_load(f)
    with open(scrape_config_file) as f:
        scrape_config = yaml.safe_load(f)
    reddit = praw.Reddit(**auth_config["reddit_config"])
    subreddit_names = scrape_config['subreddits']
    thread_list = []

    for subreddit_name in subreddit_names:
        thread = threading.Thread(target=print_submissions, group=None, args=(reddit, subreddit_name,), daemon=True)
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()