import tkinter as tk
from tkinter import ttk, messagebox
import threading

class Roundrobin:
    COLORS = ["RED", "GREEN", "BLUE", "#ff7008", "#05ffda", "#ba88ff"] # the colors im going to use for the chart

# for main class 
    def __init__(self, root):
        self.root = root 
        self.root.title("Round Robin Super Duper Scheduler")
        self.root.geometry("700x681")

        self._build_ui()

    def _build_ui(self):
        input_frame = ttk.LabelFrame(self.root, text="Enter process details")
        input_frame.pack(fill="x", padx=10, pady=8)#using pack to make the frame fill the x axis and have padding

        ttk.Label(input_frame, text="Enter the number of processes:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.processes_entry = ttk.Entry(input_frame, width=40)
        self.processes_entry.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(input_frame, text="Enter the arrival times and separate using spaces:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.arrival_entry = ttk.Entry(input_frame, width=40)
        self.arrival_entry.grid(row=1, column=1, padx=6, pady=4)

        ttk.Label(input_frame, text="Enter the time quantum:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.quantum_entry = ttk.Entry(input_frame, width=40)
        self.quantum_entry.grid(row=2, column=1, padx=6, pady=4)

        ttk.Label(input_frame, text="Enter the burst times and separate using spaces:").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.burst_entry = ttk.Entry(input_frame, width=40)
        self.burst_entry.grid(row=3, column=1, padx=6, pady=4)

        self.run_btn = ttk.Button(input_frame, text="Run Round Robin", command=self.run_round_robin)
        self.run_btn.grid(row=4, column=0, columnspan=2, pady=8)

        table_frame = ttk.LabelFrame(self.root, text="Results")
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

#forsetting up the table
        cols = ("process", "arrival", "burst", "completion", "turnaround", "waiting")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        headers = [("process", "Process", 70), ("arrival", "Arrival Time", 100),
                ("burst", "Burst Time", 90), ("completion", "Completion Time", 120),
                ("turnaround", "Turnaround Time", 120), ("waiting", "Waiting Time", 100)]
        for col, text, w in headers: #for loop to create the table headers and set their width and alignment
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", padx=6, pady=6)

        gantt_frame = ttk.LabelFrame(self.root, text="Order of Operations")
        gantt_frame.pack(fill="x", padx=10, pady=8)
        self.canvas = tk.Canvas(gantt_frame, height=90, bg="white")
        self.canvas.pack(fill="x", padx=6, pady=6)
#textbox for the average waiting and turnaround time
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=8)
        self.avg_label = ttk.Label(bottom, text="Average Waiting Time:   Average Turnaround Time: ", font=("Ink Free", 10, "bold"))
        self.avg_label.pack(side="left")
# thread to avoid freezing
    def run_round_robin(self):
        self.run_btn.config(state="disabled")
        threading.Thread(target=self._run_round_robin_logic, daemon=True).start()
# error Handles
    def _validate_inputs(self):
        try:
            processes = int(self.processes_entry.get())
            arrival_times = list(map(int, self.arrival_entry.get().split()))
            time_quantum = int(self.quantum_entry.get())
            burst_times = list(map(int, self.burst_entry.get().split()))
        except ValueError:
            return None, "All fields must contain valid integers."

        if processes <= 0:
            return None, "The number of processes must be a positive integer."
        if len(arrival_times) != processes or len(burst_times) != processes:
            return None, "Arrival/burst times must match the number of processes."
        if any(arrivals < 0 for arrivals in arrival_times):
            return None, "Arrival times must be non-negative integers."
        if time_quantum <= 0:
            return None, "Time quantum must be a positive integer."
        if any(bursts <= 0 for bursts in burst_times):
            return None, "Burst times must be positive integers."

        return (processes, arrival_times, time_quantum, burst_times), None

    def _run_round_robin_logic(self):
        result, error = self._validate_inputs()
        if error:
            self.root.after(0, lambda: messagebox.showerror("Error", error))
            self.root.after(0, self._done)
            return

        processes, arrival_times, time_quantum, burst_times = result

#for Initialize the variables first reference punk gazer from youtube
        current_time = 0
        remaining_times = burst_times.copy()
        completion_time = [0] * processes
        waiting_times = [0] * processes
        gantt_slices = []
#while loop to calculate the waiting time and turnaround time for each process
#also keeps track of each slice so the gantt chart has smth to draw
        while True:
            done = True
            for i in range(processes):
                if remaining_times[i] > 0:
                    done = False
                    if remaining_times[i] > time_quantum:
                        start = current_time
                        current_time += time_quantum
                        remaining_times[i] -= time_quantum
                        gantt_slices.append((i, start, current_time))
                    else:
                        start = current_time
                        current_time += remaining_times[i]
                        waiting_times[i] = current_time - arrival_times[i] - burst_times[i]
                        remaining_times[i] = 0
                        completion_time[i] = current_time
                        gantt_slices.append((i, start, current_time))
            if done:
                break

        turnaround_times = [completion_time[i] - arrival_times[i] for i in range(processes)]
#display the results in the GUI
        self.root.after(0, lambda: self._display_results(processes, arrival_times, burst_times, completion_time, turnaround_times, waiting_times, gantt_slices))

    def _display_results(self, processes, arrival_times, burst_times, completion_time,turnaround_times, waiting_times, gantt_slices):
        self.tree.delete(*self.tree.get_children())
        for i in range(processes):
            self.tree.insert("", "end", values=(i + 1, arrival_times[i], burst_times[i],completion_time[i], turnaround_times[i], waiting_times[i]))

        avg_wait = sum(waiting_times) / processes
        avg_turnaround = sum(turnaround_times) / processes
        self.avg_label.config(text=f"Average Waiting Time: {avg_wait:.2f}    Average Turnaround Time: {avg_turnaround:.2f}")

        self.gantt_chart(gantt_slices)
        self._done()

    def _done(self):
        self.run_btn.config(state="normal")

    def gantt_chart(self, gantt_slices):
        #for clear chart and update
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        #drawing the chart
        width = self.canvas.winfo_width() or 661
        total = max((end for _, _, end in gantt_slices), default=0) #the end  of last process
        if total == 0:
            return
        y0, y1 = 16, 67
        scale = (width - 10) / total
        for pid, start, end in gantt_slices:
            x = 5 + start * scale
            w = (end - start) * scale
            color = self.COLORS[pid % len(self.COLORS)]
            self.canvas.create_rectangle(x, y0, x + w, y1, fill=color, outline="black")
            self.canvas.create_text(x + w / 2, (y0 + y1) / 2, text=f"P{pid + 1}", fill="white")
            self.canvas.create_text(x, y1 + 12, text=str(start), anchor="w", font=("Segoe UI", 7))
        self.canvas.create_text(5 + total * scale, y1 + 12, text=str(total), anchor="w", font=("Segoe UI", 7))


#start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = Roundrobin(root)
    root.mainloop()
