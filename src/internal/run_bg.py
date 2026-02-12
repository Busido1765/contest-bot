from bg.tasks_dev import scheduler
from time import sleep


if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started")
    while True:
        sleep(10)
        print("Scheduler is running")
