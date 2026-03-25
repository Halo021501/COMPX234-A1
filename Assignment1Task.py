"""
COMPX234-26A Assignment 1
Author: [CHEN CHUNHAO / 20243006949]
Date: 2026-03-25
Description: This program simulates a print queue system using Counting and Binary Semaphores to prevent overwriting and ensure mutual exclusion.
"""

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
            t.daemon = True
            t.start()
        for t in self.pThreads:
            t.daemon = True
            t.start()

        time.sleep(self.SIMULATION_TIME)
        self.sim_active = False
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
            self.outer.binary.acquire()
            if self.outer.print_list.head is not None:
                self.outer.print_list.queuePrint(printerID)
                self.outer.semaphore.release()
            self.outer.binary.release()

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
            print(f"Machine {id} Checking availability")
            try:
                self.outer.semaphore.acquire()
            except Exception as e:
                print("Counting semaphore acquisation failed",e)
            try:
                self.outer.binary.acquire()
            except Exception as ex:
                print("Binary acquisation failed", ex)
            print(f"Machine {id} will proceed")

        def postRequest(self, id):
            print(f"Machine {id} Releasing binary semaphore")
            self.outer.binary.release()