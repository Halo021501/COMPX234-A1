import threading
import time
import random

from printDoc import printDoc
from printList import printList

class Assignment1:
    # Simulation Initialisation parameters
    NUM_MACHINES = 50        # Number of machines that issue print requests
    NUM_PRINTERS = 5         # Number of printers in the system
    SIMULATION_TIME = 30     # Total simulation time in seconds
    MAX_PRINTER_SLEEP = 3    # Maximum sleep time for printers
    MAX_MACHINE_SLEEP = 5    # Maximum sleep time for machines

    def __init__(self):
        self.sim_active = True
        self.print_list = printList()
        self.mThreads = []
        self.pThreads = []
        self.semaphore = threading.Semaphore(self.NUM_PRINTERS)
        self.binary = threading.Semaphore(1)

    def startSimulation(self):
        for i in range(self.NUM_MACHINES):
            self.mThreads.append(self.machineThread(i, self))
        for i in range(self.NUM_PRINTERS):
            self.pThreads.append(self.printerThread(i, self))

        for t in self.mThreads:
            t.start()
        for t in self.pThreads:
            t.start()

        time.sleep(self.SIMULATION_TIME)
        self.sim_active = False
        for t in self.mThreads:
            t.join(timeout=1)
        for t in self.pThreads:
            t.join(timeout=1)
        print("Simulation Ended.")

    # Printer class
    class printerThread(threading.Thread):
        def __init__(self, printerID, outer):
            threading.Thread.__init__(self)
            self.printerID = printerID
            self.outer = outer  # Reference to the Assignment1 instance

        def run(self):
            while self.outer.sim_active:
                self.printerSleep()
                self.printDox(self.printerID)

        def printerSleep(self):
            sleepSeconds = random.randint(1, self.outer.MAX_PRINTER_SLEEP)
            time.sleep(sleepSeconds)

        def printDox(self, printerID):
            print(f"Printer ID: {printerID} : now available")
            # Print from the queue
            self.outer.print_list.queuePrint(printerID)

    # Machine class
    class machineThread(threading.Thread):
        def __init__(self, machineID, outer):
            threading.Thread.__init__(self)
            self.machineID = machineID
            self.outer = outer  # Reference to the Assignment1 instance

        def run(self):
            while self.outer.sim_active:
                self.machineSleep()
                self.isRequestSafe(self.machineID)
                self.printRequest(self.machineID)
                self.postRequest(self.machineID)

        def machineSleep(self):
            sleepSeconds = random.randint(1, self.outer.MAX_MACHINE_SLEEP)
            time.sleep(sleepSeconds)

        def printRequest(self, id):
            print(f"Machine {id} Sent a print request")
            doc = printDoc(f"My name is machine {id}", id)
            self.outer.print_list.queueInsert(doc)

        def isRequestSafe(self, id):
            self.outer.semaphore.acquire()
            self.outer.binary.acquire()

        def postRequest(self, id):
            self.outer.binary.release()