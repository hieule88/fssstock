from background_task import background

@background(schedule=2)
def runtask(taskid):
    taskid=1