import ee

# Initialize Earth Engine
ee.Initialize()

# Get all tasks
tasks = ee.batch.Task.list()

# Cancel tasks that are either READY or RUNNING
for task in tasks:
    if task.state in ['READY', 'RUNNING']:
        print(f"Canceling task: {task.config['description']} (State: {task.state})")
        task.cancel()
    else:
        print(f"Skipping task: {task.config['description']} (State: {task.state})")

print("Task cancellation complete.")
