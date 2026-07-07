# Round Robin Scheduling Algorithm 
# input for processes, arrival times,burst times and time quantum
processes = int(input("Enter the number of processes: "))
try:
    if processes <= 0:
        raise ValueError("The number of processes must be a positive integer.")
except ValueError as e:
    print(f"Error: {e}")
    exit()
arrival_times = list(map(int, input("Enter the arrival times (make sure to seperate using spaces): ").split())) #map turns the input into a list of integers ref
try:
    if len(arrival_times) != processes:
        raise ValueError("The number of arrival times must match the number of processes.")
    if any(at < 0 for at in arrival_times):
        raise ValueError("Arrival times must be non-negative integers.")
except ValueError as e:
    print(f"Error: {e}")
    exit()

time_quantum = int(input("Enter the time quantum: "))
try:
    if time_quantum <= 0:
        raise ValueError("Time quantum must be a positive integer.")
except ValueError as e:
    print(f"Error: {e}")
    exit()

burst_times = list(map(int, input("Enter the burst times (make sure to seperate using spaces): ").split())) 
try:
    if len(burst_times) != processes:       
        raise ValueError("The number of burst times must match the number of processes.")     
    if any(bt <= 0 for bt in burst_times):
        raise ValueError("Burst times must be positive integers.")  
except ValueError as e:
    print(f"Error: {e}")
    exit()

# for Initialize the variables first reference punk gazer from youtube 
current_time = 0
remaining_times = burst_times.copy()
turnaround_times = [0] * processes
completion_time = [0] * processes
waiting_times = [0] * processes

# while loop to calculate the waiting time and turnaround time for each process
while True:
    done = True # a flag to check if all processes are done
    for i in range(processes):
        if remaining_times[i] > 0: 
            done = False # if the process is not done, sets done to False
            if remaining_times[i] > time_quantum:
                current_time += time_quantum
                remaining_times[i] -= time_quantum
            else:
                current_time += remaining_times[i]
                waiting_times[i] = current_time - arrival_times[i] - burst_times[i]
                remaining_times[i] = 0
                completion_time[i] = current_time
    if done:
        break

# for calculating the turnaround times
turnaround_times = [completion_time[i] - arrival_times[i] for i in range(processes)] # calculation for turnaround time

# for printing the  results in a tapble format 
print(f"\n{'Process':<10}{'Arrival Time':<15}{'Burst Time':<12}{'Completion Time':<18}{'Turnaround Time':<18}{'Waiting Time':<15}")
print("." * 90)
for i in range(processes):
    print(f"{i + 1:<10}{arrival_times[i]:<15}{burst_times[i]:<12}{completion_time[i]:<18}{turnaround_times[i]:<18}{waiting_times[i]:<15}")

# the last pat of the code calculates the average waiting time and average turnaround time and prints them out
print(f"\nAverage Waiting Time: {sum(waiting_times) / processes:.2f}")
print(f"Average Turnaround Time: {sum(turnaround_times) / processes:.2f}")