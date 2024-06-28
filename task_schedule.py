import pythoncom
import win32com.client as st

class Task():
    def __init__(self,
                task_name: str = "Auto Email",
                task_description: str = "Tarefa agendada para executar o Auto Email",
                task_type: str = "1",
                interval: int = '1',
                days: list = [],
                start: str = "2100-01-01T08:00:00-00:00",
                end: str = "2101-01-01T08:00:00-00:00",
                exec_path:str = r'/',
                argument: str = ''
                ):
        
        self.task_name = task_name 
        self.task_description = task_description
        self.task_type = task_type # (1) -> Once, (2) -> Daily, (3) -> Weekly
        self.interval = int(interval)
        self.start = start
        self.days = days
        self.end = end
        self.exec_path = exec_path
        self.argument = argument
      

    def convert_days(self, days_list: list) -> int:
        """
        This Python function converts a list of days into a total numerical value
        based on a predefined mapping.
        
        :param days_list: The `days_list` parameter is a list containing the days of
        the week represented as integers. Each integer corresponds to a specific day
        of the week as follows:
        :type days_list: list
        :return: The function `convert_days` is returning the total value calculated
        based on the input list of days. The function converts the days into
        numerical values using a dictionary mapping each day to a specific value. It
        then sums up the values for each day in the input list and returns the total
        value. If an error occurs during the conversion process, the function will
        return 0.
        """
        try:
            if isinstance(days_list[0], str) and days_list[0].isdigit():
                for i in range(len(days_list)):
                        days_list[i] = int(days_list[i])
            
            days = {
                1 : 1,   # Sunday
                2 : 2,   # Monday
                3 : 4,   # Tuesday
                4 : 8,   # Wednesday
                5 : 16,  # Thursday
                6 : 32,  # Friday
                7 : 64   # Saturday
            }
            
            return sum(days[day] for day in days_list)

        except: return 0


    def create_task(self) -> tuple[bool, str]:
        """
        The function `create_task` creates a scheduled task using the Windows Task
        Scheduler API in Python.
        :return: The `create_task` method returns a tuple containing a boolean value
        and a string. The boolean value indicates whether the task creation was
        successful (True) or not (False), and the string provides additional
        information or an error message related to the task creation process.
        """
       
        try:
            pythoncom.CoInitialize()
            
            scheduler = st.Dispatch("Schedule.Service")
            scheduler.Connect('' or None, '' or None, '' or None, '' or None)
            self.rootFolder = scheduler.GetFolder("\\")
            
            taskDef = scheduler.NewTask(0)
            colTriggers = taskDef.Triggers
            
            # Once task
            if self.task_type == '1': 
                trigger = colTriggers.Create(1)

            # Daily task
            if self.task_type == '2': 
                trigger = colTriggers.Create(2)
                trigger.DaysInterval = self.interval
                
            # Weekle task
            if self.task_type == '3':
                trigger = colTriggers.Create(3)
                trigger.WeeksInterval = self.interval
                trigger.DaysOfWeek = self.convert_days(self.days)
            
            trigger.StartBoundary = self.start
            trigger.EndBoundary = self.end
            trigger.Enabled = True
            
            colActions = taskDef.Actions
            action = colActions.Create(0) # Task Action
            action.Path = self.exec_path  # Action path
            action.Arguments = self.argument # Argument
            
            info = taskDef.RegistrationInfo
            info.Author = 'Task Scheduler'
            info.Description = self.task_description
            
            
            taskDef.Settings.Hidden = False
            taskDef.Settings.StopIfGoingOnBatteries = False
            taskDef.Settings.Enabled = True
            
            result  = self.rootFolder.RegisterTaskDefinition(self.task_name, taskDef, 6, "", "", 0)
            return True, result
        
        except Exception as e:
            return False, e

    def task_test(self) -> bool:
        """
        The function `task_test` attempts to enable, run, and disable a task, returning
        True if successful and False if an exception occurs.
        :return: The `task_test` function is returning a boolean value. If the code
        inside the try block executes successfully without any exceptions, it will
        return `True`. Otherwise, if an exception occurs during the execution, it will
        return `False`.
        """
        try:
            
            task = self.rootFolder.GetTask(self.name)
            task.Enabled = True
            task.Run("")
            task.Enabled = False
            
            return True
        
        except: return False


    def run(self) -> tuple[bool, str]:
        try:
            status, message = self.create_task()
            
            if status:
                return True, "Success, task created! "
            
            else: 
                return False, f"Fail, an error occurred during the task creation. {message}"
            
        except Exception as e:
            return False, f"Fail, an exception occurred: {str(e)}"



if __name__ == '__main__':
    
    task = Task(
            task_name='Test task',
            task_description='Scheduled task',
            task_type='1',
            interval= '1',
            days=[1],
            start='2024-06-27T17:39:00-03:00', 
            end='', 
            exec_path= "/"
        )
    
    status, message = task.run()
    print(f"Status: {status} - {message}")

    