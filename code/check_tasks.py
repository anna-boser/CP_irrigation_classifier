import ee

def count_task_statuses():
    """Lists the number of tasks by their current status."""
    ee.Initialize()

    try:
        # Fetch all tasks
        tasks = ee.data.listOperations()
        
        # Ensure we handle the case where a list is returned
        if isinstance(tasks, list):
            tasks = {"operations": tasks}

        task_status_count = {}

        # Parse and count tasks based on their state
        for task in tasks.get('operations', []):
            state = task.get('metadata', {}).get('state', 'UNKNOWN')
            task_status_count[state] = task_status_count.get(state, 0) + 1

        # Print results
        print("Task Status Counts:")
        for status, count in task_status_count.items():
            print(f"{status}: {count}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    count_task_statuses()

