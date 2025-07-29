import asyncio
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional

class Task:
    def __init__(self, func: Callable, args: tuple = (), kwargs: dict = None,
                 interval: Optional[int] = None, start_time: Optional[datetime] = None):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.interval = interval
        self.start_time = start_time
        self.last_run = None
        self.is_running = False

    def should_run(self) -> bool:
        if self.is_running:
            return False
        if self.start_time and datetime.now() < self.start_time:
            return False
        if self.interval and self.last_run:
            return (datetime.now() - self.last_run).total_seconds() >= self.interval
        return True

    def run(self):
        self.is_running = True
        try:
            result = self.func(*self.args, **self.kwargs)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)
        except Exception as e:
            print(f"Error in task {self.func.__name__}: {str(e)}")
        finally:
            self.is_running = False
            self.last_run = datetime.now()

class TaskScheduler:
    def __init__(self):
        self.tasks: List[Task] = []
        self.running = False
        self.thread = None
        self.task_queue = queue.Queue()

    def add_task(self, func: Callable, args: tuple = (), kwargs: dict = None,
                interval: Optional[int] = None, start_time: Optional[datetime] = None) -> Task:
        task = Task(func, args, kwargs, interval, start_time)
        self.tasks.append(task)
        return task

    def remove_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        while self.running:
            for task in self.tasks:
                if task.should_run():
                    self.task_queue.put(task)
            time.sleep(1)

    def process_tasks(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            task.run()
            self.task_queue.task_done()

class BackgroundTasks:
    def __init__(self, app):
        self.app = app
        self.scheduler = TaskScheduler()

    def task(self, interval: Optional[int] = None, start_time: Optional[datetime] = None):
        def decorator(func: Callable):
            self.scheduler.add_task(func, interval=interval, start_time=start_time)
            return func
        return decorator

    def add_task(self, func: Callable, args: tuple = (), kwargs: dict = None,
                interval: Optional[int] = None, start_time: Optional[datetime] = None) -> Task:
        return self.scheduler.add_task(func, args, kwargs, interval, start_time)

    def remove_task(self, task: Task):
        self.scheduler.remove_task(task)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.stop()

    def process_tasks(self):
        self.scheduler.process_tasks() 