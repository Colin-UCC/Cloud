from random import randint
import matplotlib.pyplot as plt
import time
import numpy as np

class Queue():
        def __init__(self, priority, quantum):
            '''Initialise the stacks'''
            self.p1 = []
            self.p2 = []            
            self.priority = priority
            self.quantum = quantum

        def enqueue(self, x: int):
            ''' This steue method pushes the element x from stack 
                1 to stack 2 and back to maintain FIFO queue'''

            while self.p1:
                self.p2.append(self.p1.pop())

            self.p1.append(x)

            while self.p2:
                self.p1.append(self.p2.pop())

        def dequeue(self):
            ''' Removes the element from front of queue and returns '''
            while self.p1:
                return self.p1.pop()

        
        def top(self):
            ''' Returns the element at the front of the queue '''
            return self.p1[-1]

        def empty(self) -> bool:
            ''' Returns whether the queue is empty '''
            return not self.p1

        def length(self):
            ''' Returns the length of the queue '''
            return len(self.p1)

class Process():
    
    def __init__(self, pid, queue, state, burst_time, remaining_time, IO, IO_duration, unblocked):
        self.pid = pid
        self.queue = queue
        self.state = state
        self.burst_time = burst_time
        self.remaining_time = remaining_time
        self.IO = IO
        self.IO_duration = IO_duration
        self.unblocked = unblocked
        
    '''def __str__(self):
        output = f"{self.pid}"
        #output = f"******\nPid: {self.pid}\nQueue: {self.queue}\nState: {self.state}\nBurst Time: {self.burst_time}\nRemaining Time: {self.remaining_time}\nIO: {self.IO}\n******\n"
        return output'''


class B_Queue():
    def __init__(self, priority, IO_duration, unblocked) -> None:
        self.p1_blocked = []
        self.p2_blocked = []
        self.priority = priority
        self.IO_duration = IO_duration
        self.unblocked = unblocked

    def enqueue(self, x: int):
        ''' This method pushes the element x from stack 
            1 to stack 2 to maintain FIFO queue'''
        while self.p1_blocked:
            self.p2_blocked.append(self.p1_blocked.pop())
        self.p1_blocked.append(x)
        while self.p2_blocked:
            self.p1_blocked.append(self.p2_blocked.pop())

    def dequeue(self):
        '''Removes the element from front of queue and returns'''
        while self.p1_blocked:
            return self.p1_blocked.pop()

    def top(self):
        '''Returns the element at the front of the queue'''
        return self.p1_blocked[-1]
    def empty(self) -> bool:

        '''Returns whether the queue is empty'''
        return not self.p1_blocked

    def length(self):
        '''Returns the length of the queue'''
        return len(self.p1_blocked)

    def __str__(self):
        if len(self.p1_blocked) == 0:
            return f"Blocked Queue: >-empty->\n"
        stringlist = [f"Blocked Queue: >"]
        for item in self.p1_blocked:
            stringlist.append('-' + str(item))
        stringlist.append('->\n')
        return ''.join(stringlist)

class CPU():
    ''' This class maintains the CPU voltage, frequency and state'''
    def __init__(self, voltage, frequency, state) -> None:

        statelist = ["running", "idle", "sleep"]  
        self._voltage = voltage
        self._frequency = frequency
        self._state = state

        if voltage < 1.0 or voltage > 2.5:
            self._voltage = 1.0
              
              
        else:
            self._voltage = voltage                   
                    
        if frequency < 0.5 or frequency > 3.5:        
            self._frequency = 1.1             
        
        else:
            self._frequency = frequency                   
        
        if state not in statelist:
            self._state = "ready"
        else:
            self._state = state  
    
    def get_voltage(self):
        return self._voltage
    
    def get_frequency(self):
        return self._frequency

    def get_state(self):
        return self._state
    
    def reset_voltage(self, voltage):
        self._voltage = voltage

    def reset_frequency(self, frequency):
        self._frequency = frequency

    def reset_state(self, state):
        self._state = state

    def __str__(self) -> str:
        output = f"------------ CPU -------------\nVoltage:\t\t{self._voltage} V\nFrequency:\t\t{round(self._frequency, 3)} Ghz\nState:\t\t\t{self._state}"
        return output


class MLFQ():       

    def CPU_run(queuelist, processlist, blocked_queue, cpu):
        ''' This method takes in two lists - the priority queues and the processes ready list.
            The scheduler enqueues the processes in to the correct queues if they cannot be     
            allocated control to CPU at priority 0 '''
        p = processlist
        q = queuelist
        bq = blocked_queue

        loop_counter = 1
        clock_frequency = cpu._frequency
        power_saving_clock_fre = cpu._frequency - (cpu._frequency * .2)
        cpu._state = "running"
               
        start_time = time.perf_counter()

        def enqueue_proc(process):
            q[0].enqueue(process)

        def _top_execute():
            ''' This method is the main method of the CPU execution on the top of any queue.
                Makes necessary comparisons before dequeueing or blocking'''
            if not bq.empty():
                store_val = bq.top().IO_duration
            if q.top().IO:        
                blocked_process = q.top()                
                duration = blocked_process.IO_duration
                blocked_process.state = "blocked"                
                blocked_queue.enqueue(blocked_process)
            if q.top().remaining_time < q.quantum and q.top().state == "ready":
                    qp = q.priority
                    temp_val = q.top().remaining_time                   
                    q.dequeue()
                    if not bq.empty():
                        
                        time_left = bq.top().IO_duration - temp_val                        
                        if time_left <= 0:
                            bq.top().state = "ready"
                            bq.top().IO = False                            
                            if qp >= 0:
                                queuelist[qp -1].enqueue(bq.top())
                            else:
                                queuelist[0].enqueue(bq.top())
                            bq.dequeue()
                            blocked_queue.unblocked = True
                            if not bq.empty():
                                bq.top().IO_duration = store_val - abs(time_left)                                
                                                        
            elif q.top().remaining_time > q.quantum and q.top().state == "ready":
                    qp = q.priority
                    q.top().remaining_time -= q.quantum
                    current_queue = q
                    proc_d = q.top()
                    if q.priority == 7:
                        cpu.reset_frequency(power_saving_clock_fre)
                        _top_execute()
                    else:
                        next_q = queuelist[current_queue.priority + 1]                      
                        current_queue.dequeue()
                        next_q.enqueue(proc_d)
                        if not bq.empty():                            
                            time_left = bq.top().IO_duration - q.quantum
                            bq.top().IO_duration = time_left
                            if time_left > 0:                               
                                pass
                            if time_left <= 0:
                                bq.top().state = "ready"
                                bq.top().IO = False                               
                                if qp >= 0:
                                    queuelist[qp - 1].enqueue(bq.top())
                                else:
                                    queuelist[0].enqueue(bq.top())
                                bq.top().IO_duration = 0
                                bq.dequeue()
                                blocked_queue.unblocked = True
                                if not bq.empty():
                                    bq.top().IO_duration = store_val - abs(time_left)                                                     
            else:
                q.dequeue()

        # schedule loop        
        for proc in p:
            enqueue_proc(proc)                       

        def printloop():

            ''' This method prints out debugging data for the cpu execution loop'''
            
            if q.priority == 7:
                cpu.reset_frequency(power_saving_clock_fre)
            else:
                pass

        def end_loop():

            ''' This method switches cpu to idle once all processes have been terminated '''

            counter = 0
            for i in range(7):

                if blocked_queue.length() == 0:
                    if queuelist[i].length() == 0:
                        counter += 1
            if counter == 7:
                cpu._voltage = 1.0
                cpu._frequency = 1.4
                cpu._state = "idle"
                end_time = time.perf_counter()
                total_time = end_time - start_time
                return True

        # MAIN LOOP

        ''' This loop traverses the queuelist and makes the necessary actions on each process '''   

        main_loop = True
        inner_loop = False
        while main_loop:
            for q in queuelist:
                    inner_loop = False                    
                    while not q.empty():
                        if blocked_queue.unblocked == True:
                            blocked_queue.unblocked = False
                            inner_loop = True
                            break
                        previous_proc_burst = q.top().burst_time
                        prev_proc_remain = q.top().remaining_time
                                    
                        _top_execute()
                        loop_counter += 1                                                  
                    if inner_loop == True:
                        break
            if end_loop():            
                break

def test():
    #q priority and quantum
    q0 = Queue(0, 10)
    q1 = Queue(1, 20)
    q2 = Queue(2, 40)
    q3 = Queue(3, 80)
    q4 = Queue(4, 160)
    q5 = Queue(5, 320)
    q6 = Queue(6, 640)
    q7 = Queue(7, 1536)

    # blocked process queue
    qb = B_Queue(0, 0, False)

    qlist = [q0, q1, q2, q3, q4, q5, q6, q7]
    testlist = []
    ypoints = []

    #n = [100,200,300,400,500,600,700,800,900,1000]
    n = [300, 500, 800, 1000, 1500]

    for j in range(len(n)):
        for i in range(n[j]):
            io = True
            timer =randint(1,200)
            number = randint(1,13)
            if number < 10:
                io = False
            process = Process(i, 0, "ready", timer, timer, io, timer//.5, False)
            testlist.append(process)
        cpu = CPU(1.5, 2.1, "idle")
        test_start = time.perf_counter()
        MLFQ.CPU_run(qlist, testlist, qb, cpu)
        test_end = time.perf_counter()
        time_result = round((test_end - test_start),3)
        print(f"Total Time:\t{time_result}s")
        ypoints.append(time_result)
    
    '''for j in range(len(n_)):
        for i in range(n_[j]):
            io = True
            timer =randint(1,200)
            number = randint(1,13)
            if number < 10:
                io = False
            process = Process(i, 0, "ready", timer, timer, io, timer//.5, False)
            testlist.append(process)
        cpu = CPU(1.5, 2.1, "idle")
        test_start = time.perf_counter()
        MLFQ.CPU_run(qlist, testlist, qb, cpu)
        test_end = time.perf_counter()
        time_result = round((test_end - test_start),3)
        print(f"Total Time:\t{time_result}s")
        ypoints.append(time_result)'''
    
    plt.plot(n, ypoints, marker = 'o')
    plt.xlabel("N")
    plt.ylabel("Seconds")
    plt.savefig("plot.png")
    plt.show()
    plt.close()

if __name__ == '__main__':
    test()