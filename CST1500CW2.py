import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
 
 
class Process:
    # just holds the data, scheduler fills in waiting_time later
    def __init__(self, pid, burst_time):
        self.pid = pid
        self.burst_time = burst_time
        self.waiting_time = 0
 
 
class SJFApp:
    # A palette of colors used for the Gantt chart bars
    COLORS = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759",
              "#76b7b2", "#edc948", "#b07aa1", "#ff9da7"]
 
    def __init__(self, root):
        self.root = root
        self.root.title("SJF Scheduler")
        self.root.geometry("640x640")
 
        self.processes = []
        self.next_pid = 1  # pids auto-assigned -> no duplicates
        self.running = False  # guard so you can't start two runs at once
 
        self._build_ui()
 
    # ---------- UI construction ----------
    def _build_ui(self):
        # 4 sections top to bottom: input -> table -> gantt -> run/avg bar
        input_frame = ttk.LabelFrame(self.root, text="Add a process")
        input_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(input_frame, text="Burst time:").pack(side="left", padx=6, pady=6)
        self.burst_entry = ttk.Entry(input_frame, width=10)
        self.burst_entry.pack(side="left", padx=6)
        self.burst_entry.bind("<Return>", lambda e: self.add_process())  # enter = add
        ttk.Button(input_frame, text="Add", command=self.add_process).pack(side="left", padx=6)
        ttk.Button(input_frame, text="Clear all", command=self.clear_all).pack(side="left", padx=6)
 
       
        table_frame = ttk.LabelFrame(self.root, text="Processes")
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)
 
        cols = ("pid", "burst", "waiting", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        for col, text, w in (("pid", "Process ID", 90),
                             ("burst", "Burst Time", 90),
                             ("waiting", "Waiting Time", 100),
                             ("status", "Status", 120)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")
 
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)
 
        # --- Gantt chart canvas ---
        gantt_frame = ttk.LabelFrame(self.root, text="Execution order (Gantt)")
        gantt_frame.pack(fill="x", padx=10, pady=8)
        self.canvas = tk.Canvas(gantt_frame, height=90, bg="white")
        self.canvas.pack(fill="x", padx=6, pady=6)
 
     
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=8)
 
        self.run_btn = ttk.Button(bottom, text="Run SJF", command=self.run_sjf)
        self.run_btn.pack(side="left")
 
        self.avg_label = ttk.Label(bottom, text="Average Waiting Time: -",
                                   font=("Segoe UI", 10, "bold"))
        self.avg_label.pack(side="right")
 
    def add_process(self):
        raw = self.burst_entry.get().strip()
        # reject anything that isn't a whole number > 0
        if not raw.isdigit() or int(raw) <= 0:
            messagebox.showerror("Invalid input",
                                 "Burst time must be a whole number greater than 0.")
            return
        p = Process(self.next_pid, int(raw))
        self.processes.append(p)
        # iid = pid, so rows can be looked up by pid later
        self.tree.insert("", "end", iid=str(p.pid),
                         values=(p.pid, p.burst_time, "-", "waiting"))
        self.next_pid += 1
        self.burst_entry.delete(0, "end")
        self.burst_entry.focus()
 
    def clear_all(self):
        if self.running:  # don't wipe the table mid-simulation
            return
        self.processes.clear()
        self.next_pid = 1
        self.tree.delete(*self.tree.get_children())
        self.canvas.delete("all")
        self.avg_label.config(text="Average Waiting Time: -")
 
    def run_sjf(self):
        if self.running:
            return
        if not self.processes:
            messagebox.showinfo("No processes", "Add at least one process first.")
            return
 
        # SJF happens here: shortest burst first
        self.processes.sort(key=lambda x: x.burst_time)
        current_time = 0
        total_waiting = 0
        for p in self.processes:
            p.waiting_time = current_time     # wait = the time you start
            total_waiting += current_time
            current_time += p.burst_time      # clock moves past this process
 
        # schedule is fully decided at this point, so results go up
        # before the animation even starts
        self.tree.delete(*self.tree.get_children())
        for p in self.processes:
            self.tree.insert("", "end", iid=str(p.pid),
                             values=(p.pid, p.burst_time, p.waiting_time, "waiting"))
 
        self.draw_gantt()
 
        avg = total_waiting / len(self.processes)
        self.avg_label.config(text=f"Average Waiting Time: {avg:.2f}")
 
        self.running = True
        self.run_btn.config(state="disabled")
        # sleeps happen on a worker thread so the window doesn't freeze
        worker = threading.Thread(target=self._simulate, daemon=True)
        worker.start()
 
    def _simulate(self):
        # just acts out the schedule, all the maths is already done
        for p in self.processes:
            # pid=p.pid pins down this process, otherwise every callback
            # would end up pointing at the last one
            self._ui(lambda pid=p.pid: self.tree.set(str(pid), "status", "running"))
            time.sleep(p.burst_time / 5)  # simulate the CPU burst (scaled)
            self._ui(lambda pid=p.pid: self.tree.set(str(pid), "status", "done"))
        self._ui(self._finish)
 
    def _finish(self):
        # unlock so it can be run again
        self.running = False
        self.run_btn.config(state="normal")
 
    def _ui(self, fn):
        # tkinter isn't thread safe -> hand updates over to the main thread
        self.root.after(0, fn)
 
    def draw_gantt(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        width = self.canvas.winfo_width() or 600
        total = sum(p.burst_time for p in self.processes)
        if total == 0:
            return
        x = 5
        y0, y1 = 15, 60
        scale = (width - 10) / total  # pixels per time unit
        for i, p in enumerate(self.processes):
            w = p.burst_time * scale  # bar width = burst time
            color = self.COLORS[i % len(self.COLORS)]  # cycle the palette
            self.canvas.create_rectangle(x, y0, x + w, y1, fill=color, outline="black")
            self.canvas.create_text(x + w / 2, (y0 + y1) / 2,
                                    text=f"P{p.pid}", fill="white")
            self.canvas.create_text(x, y1 + 12, text=str(int((x - 5) / scale)) if scale else "0",
                                    anchor="w", font=("Segoe UI", 7))
            x += w
        self.canvas.create_text(x, y1 + 12, text=str(total), anchor="w", font=("Segoe UI", 7))
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = SJFApp(root)
    root.mainloop()
