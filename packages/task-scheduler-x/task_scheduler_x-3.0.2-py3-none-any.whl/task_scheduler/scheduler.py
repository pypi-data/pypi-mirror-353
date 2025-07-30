"""! @file scheduler.py
@brief Task scheduling system implementation
@author Samuel Longauer

@defgroup scheduler Scheduler Module
@brief Core scheduling logic and data management
"""

from task_scheduler.task import Task
from task_scheduler.time_slot import TimeSlot
from task_scheduler.storage import Storage
from task_scheduler.periodic_scheduling import PeriodicScheduler
from task_scheduler.utils import time_slot_covering, set_time_to_midnight

from collections import deque
from collections import defaultdict
import bisect
import inspect
from typing import Optional, List, Dict, Any
from pathlib import Path
import difflib
import shutil
import datetime
import sys


class TaskScheduler:
    """! @brief Main task scheduling system
    @details Uses @ref Task objects with @ref TimeSlot allocations. Manages time slots, tasks, and their assignments using greedy scheduling algorithm.
    
    @ingroup scheduler
    

    """

    def __init__(self, schedule_name):
        """! @brief Initialize TaskScheduler instance
        
        @param schedule_name (str) Name identifier for the schedule
        """
        self.schedule_name = schedule_name
        self.time_slots = list()  ##< Sorted list of TimeSlot objects
        self.tasks = list()  ##< Sorted list of Task objects by deadline
        self.scheduled_tasks = defaultdict(deque)  ##< TimeSlot to Task mapping
        self.storage = Storage()

    def add_time_slot(self, time_slot):
        """! @brief Add time slot to scheduler
        @param time_slot TimeSlot object to add
        @note Maintains sorted order using bisect.insort
        """
        bisect.insort(self.time_slots, time_slot)

    def delete_time_slot(self, time_slot):
        """! @brief Remove time slot from scheduler
        @param time_slot TimeSlot object to remove
        @exception ValueError If time_slot not found
        """
        self.time_slots.remove(time_slot)

    def time_slot_management(self):
        """! @brief Clean up expired time slots
        @details Removes all time slots that have ended before current time
        """
        time_now = datetime.datetime.now()
        self.time_slots = list(filter(lambda slot: slot.end_time >= time_now, self.time_slots))

    def add_task(self, task: Optional["Task"]):
        """! @brief Add task to scheduler
        
        @param task Task object to add
        @note Maintains sorted order by deadline using bisect.insort
        @see delete_task
        """
        bisect.insort(self.tasks, task)

    def delete_task(self, task_name):
        """! @brief Remove task from scheduler
        
        @param task_name Name of task to remove
        @exception SystemExit If task not found with close match suggestions
        @see add_task
        """
        task = self.get_task_by_name(task_name)
        if not task:
            matches = difflib.get_close_matches(task_name, [t.name for t in self.tasks])
            msg = f"Task '{task_name}' not found."
            if matches:
                msg += f" Did you mean: {', '.join(matches)}?"
            print(msg, file=sys.stderr)
            sys.exit(1)

        task.duration, task.completion = 0, 0
        for ind, task in enumerate(self.tasks):
            if task.name == task_name:
                del self.tasks[ind]
            else:
                task.delete(task_name)
        self.save_schedule()

    def get_task_by_name(self, name):
        """! @brief Find task by name in hierarchy
        @param name Task name to search for
        @return Task object if found, None otherwise
        """
        return Task.find_task_by_name(name, self.tasks)

    def schedule_tasks(self, show_unscheduled=False, schedule_periodic=False):
        """! @brief Core scheduling algorithm
        
        @param show_unscheduled (bool) Whether to print unschedulable tasks
        @details Uses greedy algorithm to assign lowest-level tasks to time slots
        """
        ## always scheduling as far ahead as possible (until we run out of either time_slots or tasks)
        ## announcing impossible to schedule tasks
        ## the order subtasks must be preserved in the schedule

        ## removing all past time_slots
        self.time_slot_management()

        ## periodic scheduling
        if schedule_periodic:
            periodic_tasks = PeriodicScheduler.automatic_scheduling(self.schedule_name)
            for t in periodic_tasks:
                if all([t.name != g.name for g in self.tasks]):
                    t.deadline = set_time_to_midnight(datetime.datetime.now() + datetime.timedelta(days=1)) ## setting the deadline the same day at midnight
                    self.add_task(t)

        ## finding minimal time slot covering
        self.time_slots = time_slot_covering(self.time_slots)

        ## removing all completed top-level tasks
        self.tasks = list(filter(lambda task: task.completion < 100, self.tasks))

        ## sorting the task list
        self.tasks.sort(key=lambda task: (task.priority, task.deadline))

        ## first collect all lowest_level tasks
        lowest_level_tasks = [p for task in self.tasks for p in Task.collect_lowest_level_tasks(task)]

        ## filter out the completed tasks:
        lowest_level_tasks = list(filter(lambda task: task.completion < 100, lowest_level_tasks))

        ## filter out tasks with unset duration
        lowest_level_tasks = list(filter(lambda task: task.duration != 0, lowest_level_tasks))

        ## keep adding tasks to free time_slots until possible (while continuously checking for deadlines and time left available for the current slot)

        impossible_to_schedule = list()
        scheduling_result = dict()  ## task.name -> time_slot
        shift = 0
        iterator = iter(lowest_level_tasks)

        for ind, task in enumerate(iterator):

            for ind1, time_slot in enumerate(self.time_slots):

                ## calculating the remaining time for the current time slot
                available_time = (min(time_slot.end_time, task.deadline) - max(datetime.datetime.now(),
                                                                               time_slot.start_time)).total_seconds() / 60 - (
                                     0 if time_slot not in self.scheduled_tasks else
                                     sum([t.duration for t in self.scheduled_tasks[time_slot]]))

                task_root = task.get_root()

                if ((task.duration <= available_time) and
                        (task_root not in scheduling_result or scheduling_result[task_root] <= time_slot) and
                        (task.since <= time_slot.start_time)):

                    self.scheduled_tasks[time_slot].append(task)

                    scheduling_result[task_root] = time_slot

                    break

                else:

                    if ind1 == len(self.time_slots) - 1:

                        impossible_to_schedule.append(task.name)

                        root = task.get_root()

                        while ind + shift + 1 < len(lowest_level_tasks) and lowest_level_tasks[

                            ind + shift + 1].get_root() is root:

                            shift += 1

                            next_task = next(iterator, None)  # defensive programming ig

                            if next_task is not None:
                                impossible_to_schedule.append(next_task.name)

        if len(impossible_to_schedule) > 0 and show_unscheduled:
            print("impossible_to_schedule:", ", ".join(impossible_to_schedule), file=sys.stderr)

    def get_next_task(self):
        """! @brief Get first uncompleted task
        
        @return First uncompleted Task or None if none available
        """
        # choosing the first non-empty time_slot
        time_slot = None

        for ts in self.time_slots:

            if len(self.scheduled_tasks[ts]) > 0:
                time_slot = ts

                break

        if time_slot is None:
            print("No tasks scheduled.", file=sys.stderr)

        # extracting the first uncompleted task handle
        for task in self.scheduled_tasks[time_slot]:

            if task.completion == 100:

                continue

            return task

        return None

    def dead_tasks(self) -> List[Task]:
        """! @brief Get tasks past their deadline
        
        @return List of expired Task objects
        """
        time_now = datetime.datetime.now()

        return list(filter(lambda s: (time_now - s.deadline).total_seconds() > 0, self.tasks))

    def to_dict(self):
        """! @brief Serialize scheduler state
        
        @return Dictionary representation of scheduler state
        """
        return {
            "schedule_name": self.schedule_name,
            "time_slots": [ts.to_dict() for ts in self.time_slots],
            "tasks": [t.to_dict() for t in self.tasks],
        }

    def schedule_to_dict(self):
        """! @brief Serialize schedule assignments
        
        @return List of dictionaries representing time slot assignments
        """
        apply_to_dict = lambda x: list(map(lambda y: y.to_dict(), x))

        return [{"start_time": key.start_time.isoformat(), "end_time": key.end_time.isoformat(),
                 "tasks": list(apply_to_dict(self.scheduled_tasks[key]))} for key in self.scheduled_tasks.keys()]

    def save_schedule(self):
        """! @brief Saves to JSON files in data/{schedule_name}"""
        script_dir = Path(__file__).parent

        path = script_dir / "../data" / self.schedule_name

        path.mkdir(exist_ok=True, parents=True)

        path_to_schedule = path.joinpath("schedule.json")

        path_to_state = path.joinpath("schedule_state.json")

        self.storage.save(path_to_state, self.to_dict())

        self.storage.save(path_to_schedule, self.schedule_to_dict())

    def load_scheduler(self):
        """! @brief Load scheduler state from storage
        
        @exception FileNotFoundError If state file is missing
        """
        ## loading the initialization data from the json file
        path_to_state = Path(__file__).parent / "../data" / self.schedule_name / "schedule_state.json"

        try:
            state_json = self.storage.load(path_to_state)

        except FileNotFoundError:

            raise FileNotFoundError

        ## TaskScheduler object initialization
        self.schedule_name = state_json["schedule_name"]

        self.time_slots = list(map(lambda time_slot: TimeSlot(datetime.datetime.fromisoformat(time_slot["start_time"]),
                                                              datetime.datetime.fromisoformat(time_slot["end_time"])),
                                   state_json["time_slots"]))
        self.tasks = Task.construct_tasks(state_json["tasks"])

    def load_schedule(self):
        """! @brief Load schedule assignments from storage
        
        @exception FileNotFoundError If schedule file is missing
        """
        ##loading the schedule data from the json file
        path_to_schedule = Path(__file__).parent / "../data" / self.schedule_name / "schedule.json"

        try:
            schedule_json = self.storage.load(path_to_schedule)

        except FileNotFoundError:

            raise FileNotFoundError

        ## schedule initialization

        for slot in schedule_json:
            self.scheduled_tasks[TimeSlot(datetime.datetime.fromisoformat(slot["start_time"]),
                                          datetime.datetime.fromisoformat(slot["end_time"]))] = deque(
                Task.construct_tasks(slot["tasks"]))

    @staticmethod
    def delete_schedule(schedule_name):
        """! @brief Permanently remove schedule
        
        @param schedule_name Name of schedule to delete
        """
        script_dir = Path(__file__).parent

        schedule_dir = script_dir / "../data" / schedule_name

        shutil.rmtree(schedule_dir)

    @staticmethod
    def merge_schedules(new_schedule_name, *args):
        """! @brief Combine multiple schedules
        
        @param new_schedule_name Name for merged schedule
        @param args Names of schedules to merge
        """
        schedulers = [TaskScheduler(name) for name in args]

        ## loading the schedulers
        for scheduler in schedulers:
            scheduler.load_scheduler()

        ## collect tasks and slots
        joint_tasks = set([task for scheduler in schedulers for task in scheduler.tasks])
        joint_time_slots = [time_slot for scheduler in schedulers for time_slot in scheduler.time_slots]

        result_scheduler = TaskScheduler(new_schedule_name)

        result_scheduler.tasks = joint_tasks

        result_scheduler.time_slots = time_slot_covering(joint_time_slots)

        ## saving the schedule
        result_scheduler.save_schedule()


def main():
    ...


if __name__ == "__main__":
    main()
