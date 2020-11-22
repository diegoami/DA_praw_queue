import yaml
import praw
import threading
import json
import os
from kafka import KafkaProducer
MAX_SUBMITTED=1000
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)


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

    scrape_config_file = 'scrape.yml'
    reddit_config = {k: os.environ[k] for k in ['client_id', 'client_secret', 'password', 'user_agent', 'username']}
    kafka_config = {k: os.environ[k] for k in ['host', 'port', 'topic']}
    subreddit_names = os.environ['subreddits'].split(',')
    print(f'kafka_config: {kafka_config}')
    print(f'reddit_config: {reddit_config}')
    print(f'subreddit_names: {subreddit_names}')

    producer = KafkaProducer(bootstrap_servers=f'{kafka_config["host"]}:{kafka_config["port"]}',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    topic = kafka_config["topic"]
    reddit = praw.Reddit(**reddit_config)
    thread_list = []
    for subreddit_name in subreddit_names:
        thread = threading.Thread(target=print_submissions, group=None, args=(reddit, subreddit_name, kafka_submission), daemon=True)
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()