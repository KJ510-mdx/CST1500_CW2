from tkinter import *
from tkinter import messagebox

def calc_waiting_time(num_processes,burst_time, waiting_time):
    waiting_time[0] = 0 #no waiting time for first process
    
    #current process waits for running one to finish
    for i in range(1,num_processes):
        waiting_time[i] = burst_time[i-1] + waiting_time[i-1]

def calc_turnAround_time(num_processes,burst_time,waiting_time,turnAround_time):
    #turnAroundtime = burst_time + waiting_time
    for i in range(num_processes):
        turnAround_time[i] = burst_time[i] + waiting_time[i]

def calc_average_time(num_processes,burst_time_list,arrival_time_list):
    #assigning results in lists
    waiting_time = [0] * num_processes
    turnAround_time =[0] * num_processes
    completion_time = [0] * num_processes

    total_waiting_time = 0
    total_turnAround_time = 0
    current_time = 0
    gantt_chart = []

#arrival time logic
    for i in range(num_processes):
        arrival_time= arrival_time_list[i]
        burst_time= burst_time_list[i]

        if current_time < arrival_time:
            gantt_chart.append(["Idle", current_time, arrival_time])
            current_time = arrival_time

        start_time = current_time
        current_time = current_time + burst_time
        end_time = current_time

        completion_time[i] = end_time
        turnAround_time[i] = end_time - arrival_time
        waiting_time[i] = turnAround_time[i] - burst_time
        gantt_chart.append([f"P{i+1}", start_time, end_time])

    #totals
    for i in range(num_processes):
        total_waiting_time = total_waiting_time +waiting_time[i]
        total_turnAround_time = total_turnAround_time +turnAround_time[i]

        #calculating all average times
    average_waiting_time = total_waiting_time/num_processes
    average_turnAround_time = total_turnAround_time/num_processes
    
    return waiting_time,turnAround_time,completion_time,average_waiting_time,average_turnAround_time,gantt_chart

#displaying using gui
root = Tk()
root.title("FCFS Scheduling")
root.geometry('650x500')

Label(root, text="Enter number of processes:").grid(row=0, column=0, padx=10,pady=10)
num_entry = Entry(root, width=5)
num_entry.grid(row=0, column=1, padx=10, pady=10)

arrival_entry_list = []
burst_entry_list = []
burst_frame = Frame(root)
burst_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

def create_fields():
    global arrival_entry_list,burst_entry_list
    for widget in burst_frame.winfo_children():
        widget.destroy()
    burst_entry_list.clear()
    arrival_entry_list.clear()

#handling value errors
    try:
        num = int(num_entry.get())
        if num <=0:
            messagebox.showerror("Error","Please enter values greater than 0")
            return
    except ValueError:
        messagebox.showerror("Error", "Please enter a positive integer")
        return
    
    Label(burst_frame, text="Process", bg="yellow", width=12, borderwidth=1, relief="solid").grid(row=0, column=0)
    Label(burst_frame, text="Arrival Time", bg="lightgreen", width=12, borderwidth=1, relief="solid").grid(row=0, column=1)
    Label(burst_frame, text="Burst Time", bg="lightcoral", width=12, borderwidth=1, relief="solid").grid(row=0, column=2)
    
    for i in range(num):
        Label(burst_frame,text=f"P{i+1}", width=12, borderwidth=1, relief="solid").grid(row=i +1, column=0)

        arrival_entry = Entry(burst_frame, width=12, justify="center")
        arrival_entry.grid(row=i+1, column=1)
        arrival_entry_list.append(arrival_entry)

        burst_entry = Entry(burst_frame, width=12, justify="center")
        burst_entry.grid(row=i+1, column=2)
        burst_entry_list.append(burst_entry)     

#adding buttons
Button(root, text="Generate",command=create_fields, bg="green", fg="white").grid(row=0, column=2, padx=10, pady=10)

result = Text(root, height=16, width=70, font=("Courier", 10))
result.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

def calculate():
    if len(arrival_entry_list) == 0:
        messagebox.showwarning("Please click Generate first")
        return
    
    arrival_time_list = []
    burst_time_list = []
    num = len(arrival_entry_list)


    for i in range(num):
        try:
            arrival_time = int(arrival_entry_list[i].get())
            burst_time = int(burst_entry_list[i].get())
            if arrival_time < 0 or burst_time <=0:
                messagebox.showerror(f"Please enter arrival greater than 0 and burst time for P{i+1}")
                return
            arrival_time_list.append(arrival_time)
            burst_time_list.append(burst_time)
        except ValueError:
            messagebox.showerror("Error","Please enter valid numbers only")
            return
        
    
    waiting_time,turnAround_time,completion_time,average_waiting_time,average_turnAround_time,gantt_chart = calc_average_time(num,burst_time_list,arrival_time_list)
            
    result.delete(1.0, END)
    result.insert(END, f"{'Process': <12}{'Arrival Time': <14}{'Burst Time': <10}\n")
    result.insert(END, "-"*38+"\n")
    
    for i in range(num):
        result.insert(END,f"P{i+1:<11}{arrival_time_list[i]:<14}{burst_time_list[i]:<10}\n")
     
     #results on table  
    result.insert(END,"\n" + "-"*50 + "\n")
    result.insert(END, f"{'Process': <10}{'Waiting': <10}{'TurnAround': <12}{'Completion'}\n")
    result.insert(END, "-"*50 + "\n")

    for i in range(num):
        result.insert(END, f"P{i+1: <9}{waiting_time[i]: <10}{turnAround_time[i]: <12}{completion_time[i]}\n")

    result.insert(END, f"\nAvg WaitTime: {average_waiting_time:.2f}\n")
    result.insert(END,f"Avg TurnAroundTime: {average_turnAround_time:.2f}\n\n")

#chart
    result.insert(END, "Gantt Chart:\n")
    gantt_line = "|"
    time_line = ""
    for name, start_time, end_time in gantt_chart:
        gantt_line += f" {name} |"
        time_line += f"{start_time}"
    time_line += f"{gantt_chart[-1][2]}"
    result.insert(END, gantt_line + "\n")
    result.insert(END, time_line + "\n")
    result.insert(END, "\nFCFS Scheduling")

Button(root, text="Calculate", command=calculate, bg="blue", fg="white", font=("Arial", 11, "bold")).grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()






