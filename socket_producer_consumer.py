import socket
import threading
import time
import json
import os
from pathlib import Path
import random

from it_student import ITStudent

# Configuration
HOST = 'localhost'
BUFFER_PORT = 5000
PRODUCER_PORT = 5001
CONSUMER_PORT = 5002
BUFFER_SIZE = 10

class BufferServer:
    """Central buffer server managing the queue."""
    
    def __init__(self, host=HOST, port=BUFFER_PORT, max_size=BUFFER_SIZE):
        self.host = host
        self.port = port
        self.max_size = max_size
        self.buffer = []
        self.lock = threading.Lock()
        self.running = True
        self.shared_dir = "shared_files_socket"
        Path(self.shared_dir).mkdir(exist_ok=True)
    
    def handle_client(self, client_socket, address):
        """Handle client requests (producer or consumer)."""
        try:
            data = client_socket.recv(4096).decode('utf-8')
            request = json.loads(data)
            
            command = request.get('command')
            response = {}
            
            with self.lock:
                if command == 'PRODUCE':
                    if len(self.buffer) < self.max_size:
                        file_num = request.get('file_number')
                        xml_data = request.get('xml_data')
                        
                        # Save XML file
                        filepath = os.path.join(self.shared_dir, f"student{file_num}.xml")
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(xml_data)
                        
                        self.buffer.append(file_num)
                        response = {
                            'status': 'SUCCESS',
                            'message': f'Added student{file_num}.xml',
                            'buffer_size': len(self.buffer)
                        }
                        print(f"[BUFFER] Produced: student{file_num}.xml (Buffer: {len(self.buffer)}/{self.max_size})")
                    else:
                        response = {
                            'status': 'FULL',
                            'message': 'Buffer is full',
                            'buffer_size': len(self.buffer)
                        }
                
                elif command == 'CONSUME':
                    if self.buffer:
                        file_num = self.buffer.pop(0)
                        filepath = os.path.join(self.shared_dir, f"student{file_num}.xml")
                        
                        # Read XML file
                        if os.path.exists(filepath):
                            with open(filepath, 'r', encoding='utf-8') as f:
                                xml_data = f.read()
                            os.remove(filepath)
                            
                            response = {
                                'status': 'SUCCESS',
                                'file_number': file_num,
                                'xml_data': xml_data,
                                'buffer_size': len(self.buffer)
                            }
                            print(f"[BUFFER] Consumed: student{file_num}.xml (Buffer: {len(self.buffer)}/{self.max_size})")
                        else:
                            response = {
                                'status': 'ERROR',
                                'message': 'File not found'
                            }
                    else:
                        response = {
                            'status': 'EMPTY',
                            'message': 'Buffer is empty',
                            'buffer_size': 0
                        }
                
                elif command == 'STATUS':
                    response = {
                        'status': 'SUCCESS',
                        'buffer_size': len(self.buffer),
                        'buffer_max': self.max_size
                    }
            
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"[BUFFER] Error: {e}")
        finally:
            client_socket.close()
    
    def start(self):
        """Start the buffer server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        server_socket.settimeout(1.0)
        
        print(f"[BUFFER] Server started on {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[BUFFER] Error: {e}")
        
        server_socket.close()
        print("[BUFFER] Server stopped")


class Producer:
    """Producer client that generates and sends student data."""
    
    def __init__(self, buffer_host=HOST, buffer_port=BUFFER_PORT, count=10):
        self.buffer_host = buffer_host
        self.buffer_port = buffer_port
        self.count = count
    
    def send_request(self, request):
        """Send request to buffer server."""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.buffer_host, self.buffer_port))
            client_socket.send(json.dumps(request).encode('utf-8'))
            response = client_socket.recv(4096).decode('utf-8')
            client_socket.close()
            return json.loads(response)
        except Exception as e:
            print(f"[PRODUCER] Connection error: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    def produce(self):
        """Produce student data."""
        print("[PRODUCER] Started")
        
        for i in range(1, self.count + 1):
            # Generate student
            student = ITStudent()
            xml_data = student.to_xml()
            
            # Try to add to buffer
            while True:
                request = {
                    'command': 'PRODUCE',
                    'file_number': i,
                    'xml_data': xml_data
                }
                response = self.send_request(request)
                
                if response['status'] == 'SUCCESS':
                    print(f"[PRODUCER] Produced student{i}.xml")
                    break
                elif response['status'] == 'FULL':
                    print(f"[PRODUCER] Buffer full, waiting...")
                    time.sleep(1)
                else:
                    print(f"[PRODUCER] Error: {response.get('message')}")
                    break
            
            time.sleep(random.uniform(0.5, 1.5))
        
        print("[PRODUCER] Finished")


class Consumer:
    """Consumer client that reads and processes student data."""
    
    def __init__(self, buffer_host=HOST, buffer_port=BUFFER_PORT, count=10):
        self.buffer_host = buffer_host
        self.buffer_port = buffer_port
        self.count = count
        self.consumed = 0
    
    def send_request(self, request):
        """Send request to buffer server."""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.buffer_host, self.buffer_port))
            client_socket.send(json.dumps(request).encode('utf-8'))
            response = client_socket.recv(8192).decode('utf-8')
            client_socket.close()
            return json.loads(response)
        except Exception as e:
            print(f"[CONSUMER] Connection error: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    def consume(self):
        """Consume student data."""
        print("[CONSUMER] Started")
        
        while self.consumed < self.count:
            request = {'command': 'CONSUME'}
            response = self.send_request(request)
            
            if response['status'] == 'SUCCESS':
                xml_data = response['xml_data']
                file_num = response['file_number']
                
                # Process student
                student = ITStudent.from_xml(xml_data)
                print(f"[CONSUMER] Consumed student{file_num}.xml")
                student.display_info()
                
                self.consumed += 1
            elif response['status'] == 'EMPTY':
                print(f"[CONSUMER] Buffer empty, waiting...")
                time.sleep(1)
            else:
                print(f"[CONSUMER] Error: {response.get('message')}")
                time.sleep(1)
            
            time.sleep(random.uniform(1.0, 2.0))
        
        print(f"[CONSUMER] Finished (Processed {self.consumed} students)")


def run_socket_system():
    """Run the complete socket-based producer-consumer system."""
    print("\n" + "="*60)
    print("SOCKET-BASED PRODUCER-CONSUMER SYSTEM")
    print("="*60 + "\n")
    
    # Start buffer server
    buffer_server = BufferServer()
    buffer_thread = threading.Thread(target=buffer_server.start)
    buffer_thread.start()
    
    time.sleep(1)  # Wait for server to start
    
    # Start producer and consumer
    producer = Producer(count=10)
    consumer = Consumer(count=10)
    
    producer_thread = threading.Thread(target=producer.produce)
    consumer_thread = threading.Thread(target=consumer.consume)
    
    producer_thread.start()
    consumer_thread.start()
    
    # Wait for completion
    producer_thread.join()
    consumer_thread.join()
    
    # Stop buffer server
    buffer_server.running = False
    buffer_thread.join()
    
    print("\n" + "="*60)
    print("SOCKET SYSTEM COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        run_socket_system()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted by user")