class Process:
    def __init__(self, pid, burst_time): # Represents a process with its ID and CPU burst time
        self.pid = pid
        self.burst_time = burst_time

def sjf_scheduling(processes):
    processes.sort(key=lambda x: x.burst_time)  # Sort processes by burst time
    total_processes = len(processes)
    current_time = 0
    waiting_time = 0
    
    print("Process ID\tBurst Time\tWaiting Time")
    for p in processes:
        print(f"{p.pid}\t\t{p.burst_time}\t\t{current_time}") # Print each process wait time and sort it
        waiting_time += current_time
        current_time += p.burst_time
    
    average_waiting_time = waiting_time / total_processes
    print("\nAverage Waiting Time:", average_waiting_time)

# Example usage
if __name__ == "__main__":
    processes = [Process(1, 6), Process(2, 8), Process(3, 7), Process(4, 3)]
    sjf_scheduling(processes)
    userinput_ = input ("Press Enter to exit...")
