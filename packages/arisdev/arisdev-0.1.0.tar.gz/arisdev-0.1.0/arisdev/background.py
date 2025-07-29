"""
Background tasks handler untuk ArisDev Framework
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
import schedule

class BackgroundTasks:
    """Background tasks handler untuk ArisDev Framework"""
    
    def __init__(self, app):
        """Inisialisasi background tasks
        
        Args:
            app: Framework instance
        """
        self.app = app
        self.tasks: Dict[str, Callable] = {}
        self.scheduled_tasks: Dict[str, schedule.Job] = {}
        self.interval_tasks: Dict[str, asyncio.Task] = {}
        self.one_time_tasks: List[asyncio.Task] = []
        self.running = False
        self.thread = None
    
    def task(self, name: str = None):
        """Decorator untuk menambahkan task
        
        Args:
            name (str): Task name
        """
        def decorator(func: Callable):
            task_name = name or func.__name__
            self.tasks[task_name] = func
            return func
        return decorator
    
    def scheduled(self, cron: str):
        """Decorator untuk menambahkan scheduled task
        
        Args:
            cron (str): Cron expression
        """
        def decorator(func: Callable):
            task_name = func.__name__
            self.scheduled_tasks[task_name] = schedule.every().day.at(cron).do(func)
            return func
        return decorator
    
    def interval(self, seconds: int):
        """Decorator untuk menambahkan interval task
        
        Args:
            seconds (int): Interval in seconds
        """
        def decorator(func: Callable):
            task_name = func.__name__
            self.interval_tasks[task_name] = asyncio.create_task(self._run_interval(func, seconds))
            return func
        return decorator
    
    def one_time(self, func: Callable, *args, **kwargs):
        """Add one-time task
        
        Args:
            func (callable): Task function
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        task = asyncio.create_task(func(*args, **kwargs))
        self.one_time_tasks.append(task)
        return task
    
    async def _run_interval(self, func: Callable, seconds: int):
        """Run interval task
        
        Args:
            func (callable): Task function
            seconds (int): Interval in seconds
        """
        while self.running:
            try:
                await func()
            except Exception as e:
                self.app.logger.error(f"Error in interval task {func.__name__}: {str(e)}")
            await asyncio.sleep(seconds)
    
    def _run_scheduled(self):
        """Run scheduled tasks"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """Start background tasks"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduled)
            self.thread.start()
    
    def stop(self):
        """Stop background tasks"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            
            # Cancel interval tasks
            for task in self.interval_tasks.values():
                task.cancel()
            
            # Cancel one-time tasks
            for task in self.one_time_tasks:
                task.cancel()
            
            # Clear scheduled tasks
            schedule.clear()
    
    def get_task(self, name: str) -> Callable:
        """Get task by name
        
        Args:
            name (str): Task name
        """
        return self.tasks.get(name)
    
    def get_scheduled_task(self, name: str) -> schedule.Job:
        """Get scheduled task by name
        
        Args:
            name (str): Task name
        """
        return self.scheduled_tasks.get(name)
    
    def get_interval_task(self, name: str) -> asyncio.Task:
        """Get interval task by name
        
        Args:
            name (str): Task name
        """
        return self.interval_tasks.get(name)
    
    def get_all_tasks(self) -> Dict[str, Callable]:
        """Get all tasks"""
        return self.tasks
    
    def get_all_scheduled_tasks(self) -> Dict[str, schedule.Job]:
        """Get all scheduled tasks"""
        return self.scheduled_tasks
    
    def get_all_interval_tasks(self) -> Dict[str, asyncio.Task]:
        """Get all interval tasks"""
        return self.interval_tasks
    
    def get_all_one_time_tasks(self) -> List[asyncio.Task]:
        """Get all one-time tasks"""
        return self.one_time_tasks
    
    def is_running(self) -> bool:
        """Check if background tasks are running"""
        return self.running 