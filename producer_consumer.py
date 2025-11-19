import threading
import time
import os
from queue import Queue
from pathlib import Path
import random

# Import the ITStudent class (assumes it's in the same directory)
from it_student import ITStudent

class ProducerConsumer:
    """Implementation of the Producer-Consumer problem with semaphores."""
    
    def __init__(self, buffer_size=10, shared_dir="shared_files"):
        self.buffer_size = buffer_size
        self.buffer = Queue(maxsize=buffer_size)
        self.shared_dir = shared_dir
        
        # Create shared directory if it doesn't exist
        Path(self.shared_dir).mkdir(exist_ok=True)
        
        # Semaphores for synchronization
        self.mutex = threading.Semaphore(1)  # Mutual exclusion
        self.empty = threading.Semaphore(buffer_size)  # Count empty slots
        self.full = threading.Semaphore(0)  # Count full slots
        
        # Control flags
        self.is_producing = True
        self.production_count = 0
        self.max_production = 10  # Produce 10 students
    
    def producer(self):
        """Producer thread: generates student data and stores as XML."""
        print("[PRODUCER] Started")
        
        for i in range(1, self.max_production + 1):
            # Generate student data
            student = ITStudent()
            xml_data = student.to_xml()
            filename = f"student{i}.xml"
            filepath = os.path.join(self.shared_dir, filename)
            
            # Wait for empty slot
            self.empty.acquire()
            
            # Critical section - mutual exclusion
            self.mutex.acquire()
            try:
                # Write XML file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(xml_data)
                
                # Add file number to buffer
                self.buffer.put(i)
                self.production_count += 1
                
                print(f"[PRODUCER] Produced: {filename} (Buffer size: {self.buffer.qsize()})")
                
            finally:
                self.mutex.release()
            
            # Signal that buffer has item
            self.full.release()
            
            # Simulate production time
            time.sleep(random.uniform(0.5, 1.5))
        
        self.is_producing = False
        print("[PRODUCER] Finished production")
    
    def consumer(self):
        """Consumer thread: reads XML files and processes student data."""
        print("[CONSUMER] Started")
        consumed_count = 0
        
        while self.is_producing or not self.buffer.empty():
            # Wait for full slot
            self.full.acquire()
            
            # Critical section - mutual exclusion
            self.mutex.acquire()
            try:
                # Get file number from buffer
                file_number = self.buffer.get()
                filename = f"student{file_number}.xml"
                filepath = os.path.join(self.shared_dir, filename)
                
                print(f"[CONSUMER] Consuming: {filename} (Buffer size: {self.buffer.qsize()})")
                
                # Read XML file
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                    
                    # Parse student information
                    student = ITStudent.from_xml(xml_content)
                    
                    # Display student information
                    student.display_info()
                    
                    # Delete the file
                    os.remove(filepath)
                    consumed_count += 1
                else:
                    print(f"[CONSUMER] ERROR: File {filename} not found!")
                
            finally:
                self.mutex.release()
            
            # Signal that buffer has empty slot
            self.empty.release()
            
            # Simulate consumption time
            time.sleep(random.uniform(1.0, 2.0))
        
        print(f"[CONSUMER] Finished consumption (Processed {consumed_count} students)")
    
    def run(self):
        """Start producer and consumer threads."""
        print("\n" + "="*60)
        print("PRODUCER-CONSUMER PROBLEM SIMULATION")
        print(f"Buffer Size: {self.buffer_size}")
        print(f"Students to Process: {self.max_production}")
        print("="*60 + "\n")
        
        # Create threads
        producer_thread = threading.Thread(target=self.producer, name="Producer")
        consumer_thread = threading.Thread(target=self.consumer, name="Consumer")
        
        # Start threads
        producer_thread.start()
        consumer_thread.start()
        
        # Wait for threads to complete
        producer_thread.join()
        consumer_thread.join()
        
        print("\n" + "="*60)
        print("SIMULATION COMPLETED")
        print("="*60 + "\n")
    
    def cleanup(self):
        """Clean up shared directory."""
        for file in Path(self.shared_dir).glob("student*.xml"):
            file.unlink()
        print(f"[CLEANUP] Removed all XML files from {self.shared_dir}")


if __name__ == "__main__":
    # Create and run producer-consumer system
    pc_system = ProducerConsumer(buffer_size=10)
    
    try:
        pc_system.run()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted by user")
    finally:
        pc_system.cleanup()