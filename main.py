import yaml
import praw
import threading
import json
from kafka import KafkaProducer
MAX_SUBMITTED=1000

lock = threading.Lock()
submitted = []
producer = None
topic = None

def kafka_submission(subreddit_name, submission):
    global producer
    global topic
    print_submission(subreddit_name, submission)
    producer.send(topic=topic,
                  value={
                      'subreddit': subreddit_name,
                      'title': submission.title,
                      'url': submission.url})

def print_submission(subreddit_name, submission):
    print(subreddit_name)
    print(submission.title)
    print(submission.url)

def print_submissions(reddit, subreddit_name, process_submission=print_submission):
    print("STARTING THREAD "+subreddit_name)
    for submission in reddit.subreddit(subreddit_name).stream.submissions():
        global submitted
        lock.acquire()
        if (submission.url not in submitted):
            process_submission(subreddit_name, submission)
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
    kafka_config = scrape_config['kafka']
    producer = KafkaProducer(bootstrap_servers=f'{kafka_config["host"]}:{kafka_config["port"]}',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8')
                             )
    topic = kafka_config["topic"]
    reddit = praw.Reddit(**auth_config["reddit_config"])
    subreddit_names = scrape_config['subreddits']
    thread_list = []
    for subreddit_name in subreddit_names:
        thread = threading.Thread(target=print_submissions, group=None, args=(reddit, subreddit_name, kafka_submission), daemon=True)
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()