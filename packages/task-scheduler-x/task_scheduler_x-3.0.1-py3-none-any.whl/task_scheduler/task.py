"""! @file task.py
@brief Task management module with hierarchical structure
@author Samuel Longauer

@defgroup task Task Module
@brief Implements hierarchical task structure with automatic property recalculation
"""

import datetime as datetime
from copy import copy, deepcopy
from typing import Optional, Iterable, List, Dict, Any
import inspect

class Task:
    """! @brief Hierarchical task structure with deadline propagation
    
    @ingroup task
    
    Represents a task with automatic recalculation of duration and completion
    based on subtasks. Maintains parent-child relationships and deadline inheritance.
    """

    def __init__(self, name, description=None, deadline: datetime = None, 
                 duration: int = 0, parent: Optional["Task"] = None, priority: int = 0, since: datetime = None):
        """! @brief Initialize Task instance
        
        @param name Task name identifier
        @param description Optional task description
        @param deadline Optional datetime deadline (defaults to distant future)
        @param duration Initial duration in minutes (default 0)
        @param parent Parent task reference (None for root tasks)
        """
        self.name = name
        self.description = description
        self._deadline = datetime.datetime.fromisoformat("9999-12-31T23:59:59") if not deadline else deadline
        self._since = datetime.datetime.fromisoformat("0001-01-01T00:00:00") if not since else since
        self.subtasks = list()  ##< List of child Task objects
        self._duration = 0 if not duration else duration
        self._completion = 0  ##< Completion percentage (0-100)
        self.parent = parent  ##< Parent task reference
        self.priority = 0 if not priority else priority

    @property
    def deadline(self):
        """! @brief Task deadline datetime
        @note Setting propagates to all subtasks
        """
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        """! @brief Set deadline and propagate to subtasks
        @param value New datetime value for deadline
        """
        self._deadline = value

        root = self.get_root()
        root.__deadline_recalc()

    @property
    def since(self):
        """! @brief Time since scheduled - datetime
        @note Setting propagates to all subtasks
        """
        return self._since

    @since.setter
    def since(self, value):
        """! @brief Set since and propagate to subtasks
        @param value New datetime value for since
        """
        self._since = value

        root = self.get_root()
        root.__since_recalc()

    @property
    def duration(self):
        """! @brief Task duration in minutes
        @note Automatically recalculates parent durations
        """
        return self._duration

    @duration.setter
    def duration(self, value):
        """! @brief Set task duration
        @param value Non-negative duration in minutes
        @exception AssertionError If value is negative
        """
        assert value >= 0
        self._duration = value
        self.__recalc()

    @property
    def completion(self):
        """! @brief Task completion percentage (0-100)
        @note Automatically recalculates parent completions
        """
        return self._completion

    @completion.setter
    def completion(self, value):
        """! @brief Set task completion percentage
        @param value Integer between 0-100
        @exception AssertionError If value out of range
        """
        assert 0 <= value <= 100
        self._completion = value
        self.__recalc()

    def divide(self, *args, **kwargs):
        """! @brief Create and add subtask
        @details Creates new Task instance as child of this task
        @param args Positional arguments for Task constructor
        @param kwargs Keyword arguments for Task constructor
        """
        new_task = Task(*args, **kwargs)
        new_task.parent = self
        new_task.deadline = self.deadline
        new_task.priority = self.priority
        new_task.since = self.since
        self.subtasks.append(new_task)
        self.__recalc()
    
    @staticmethod
    def move(task_to_move, target_task):
        """! @brief Move task to new parent
        @param task_to_move Task instance to relocate
        @param target_task New parent task
        @note Updates parent reference and triggers recalculations
        """
        target_task.subtasks.append(task_to_move)
        task_to_move.parent = target_task
        target_task.__recalc()

    def delete(self, task_name):
        """! @brief Remove subtask by name
        @param task_name Name of subtask to remove
        @details Recursively searches subtask hierarchy
        """
        for ind, task in enumerate(self.subtasks):
            if task.name == task_name:
                del self.subtasks[ind]
            else:
                task.delete(task_name)

    def __repr__(self):
        """! @brief Official string representation
        @return String with key task attributes
        """
        return f"(name: {self.name}, deadline: {self.deadline}, duration: {self.duration}, completion: {self.completion})"

    def __hash__(self):
        """! @brief Hash based on task name
        @return Integer hash value
        """
        return hash(self.name)

    def __copy__(self):
        """! @brief Shallow copy implementation
        @return New Task instance with copied attributes
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        """! @brief Deep copy implementation
        @param memo Dictionary of already copied objects
        @return New Task instance with deep copied attributes
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo) if k != "parent" else setattr(result, k, copy(v)))
        return result

    def get_root(self):
        """! @brief Find root ancestor task
        @return Top-level parent task in hierarchy
        """
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    def __duration_recalc(self):
        """! @brief Recalculate duration from subtasks
        @return Updated duration value
        @private
        """
        if not self.subtasks:
            return self.duration
        self._duration = sum(task.__duration_recalc() for task in self.subtasks)
        return self.duration

    def __completion_recalc(self):
        """! @brief Recalculate completion from subtasks
        @return Updated completion value
        @private
        """
        if not self.subtasks:
            return self.completion
            
        if self.duration == 0:
            self._completion = 0
        else:
            weighted_sum = sum(task.completion * task.duration for task in self.subtasks)
            self._completion = weighted_sum / self.duration
        return self.completion

    def __deadline_recalc(self):
        """! @brief Propagate deadline to subtasks
        @private
        """
        for task in self.subtasks:
            task._deadline = self.deadline
            task.__deadline_recalc()

    def __since_recalc(self):
        """! @brief Propagate since to subtasks
        @private
        """
        for task in self.subtasks:
            task._since = self.since
            task.__since_recalc()

    def __recalc(self):
        """! @brief Trigger full recalculation from root
        @private
        """
        root = self.get_root()
        root.__duration_recalc()
        root.__completion_recalc()

    def to_dict(self):
        """! @brief Serialize task to dictionary
        @return Dictionary representation of task hierarchy
        """
        return {
            "name": self.name,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "since": self.since.isoformat(),
            "duration": self.duration,
            "completion": self.completion,
            "priority": self.priority,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks]
        }

    @classmethod
    def construct_tasks(cls, tasks: List[Dict[str, Any]]) -> List["Task"]:
        """! @brief Reconstruct task hierarchy from serialized data

        @param tasks List of serialized task dictionaries
        @return List of reconstructed Task objects
        """
        ## filter arguments for initialization of a Task object

        filter_dict = lambda d: {key: value for key, value in d.items() if
                                 key in inspect.signature(Task.__init__).parameters}

        filter_complement = lambda d: {key: value for key, value in d.items() if
                                       key not in inspect.signature(Task.__init__).parameters}

        constructed_tasks = list()
        for task in tasks:

            ## recursively construct the subtasks
            subtasks = cls.construct_tasks(task["subtasks"])

            ## filter out key-value pairs that are not in the argument list of the Task constructor
            filtered_arguments = filter_dict(task)

            ## filter out key-value pairs that are in the argument list of the Task constructor
            argument_list_complement = filter_complement(task)

            ##construct the datetime object from iso format
            filtered_arguments["deadline"] = datetime.datetime.fromisoformat(filtered_arguments["deadline"])

            ##construct the datetime object from iso format
            filtered_arguments["since"] = datetime.datetime.fromisoformat(filtered_arguments["since"])

            new_task = Task(**filtered_arguments)

            ## initializing the rest of the attributes (outside the constructor argument list)
            for key, value in argument_list_complement.items():
                setattr(new_task, key, value)

            new_task.subtasks = subtasks

            ## setting parent pointers to all task instances
            for t in new_task.subtasks:
                t.parent = new_task

            constructed_tasks.append(new_task)

        return constructed_tasks

    def __eq__(self, other):
        """! @brief Equality comparison
        @param other Comparison target
        @return True if same name and deadline
        """
        return isinstance(other, Task) and \
               self.deadline == other.deadline and \
               self.name == other.name

    def __lt__(self, other):
        """! @brief Less-than comparison
        @param other Comparison target
        @return True if earlier deadline
        """
        return self.deadline < other.deadline

    @staticmethod
    def find_task_by_name(name: str, container: Iterable["Task"]) -> Optional["Task"]:
        """! @brief Recursive search for task by name
        @param name Target task name
        @param container Iterable of tasks to search
        @return Found Task or None
        """
        for task in container:
            if task.name == name:
                return task
            if found := Task.find_task_by_name(name, task.subtasks):
                return found
        return None

    @staticmethod
    def collect_lowest_level_tasks(instance: Optional["Task"]):
        """! @brief Collect leaf node tasks
        @param instance Starting task for collection
        @return List of tasks without subtasks
        """
        if not instance.subtasks:
            return [instance]
        return [p for task in instance.subtasks for p in Task.collect_lowest_level_tasks(task)]


def main():
    ...

if __name__ == "__main__":
    main()
