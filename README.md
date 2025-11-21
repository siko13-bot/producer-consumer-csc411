# Producer-Consumer Problem Implementation

## CSC411 - Integrative Programming Technologies Mini Project

### Team Members

- Sikolethu Mkhabela - 202101251
- Simanga Fakudze - 202003666

### Project Overview

This project implements the classic Producer-Consumer synchronization problem in Python, featuring:

- Multi-threaded producer-consumer system with semaphores
- XML-based data serialization and deserialization
- Socket-based distributed implementation
- Automatic student data generation

---

## Project Structure

```
producer-consumer-project/
│
├── it_student.py              # ITStudent class definition
├── producer_consumer.py       # Main multi-threaded implementation
├── socket_producer_consumer.py # Socket-based implementation
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── shared_files/              # Directory for XML files (created at runtime)
└── shared_files_socket/       # Directory for socket version (created at runtime)
```

---

## Features Implemented

### Part 1: Producer-Consumer Problem [70 Marks]

#### ITStudent Class

- **Random Data Generation**: Generates realistic student data including:

  - Student Name (from Swazi name pool)
  - 8-digit Student ID
  - Programme (BSc Computer Science, IT, Software Engineering, Data Science)
  - 4-6 random courses with marks (30-100 range)

- **XML Serialization**:

  - Converts student objects to well-formatted XML
  - Parses XML back to student objects

- **Student Evaluation**:
  - Calculates average mark across all courses
  - Determines Pass/Fail status (50% threshold)
  - Displays formatted student information

#### Producer

- Generates 10 student records with random data
- Wraps each student into XML format
- Saves XML files as `student1.xml` through `student10.xml`
- Inserts corresponding integers (1-10) into the buffer
- Respects buffer capacity (waits when full)

#### Consumer

- Reads XML files from shared directory
- Unwraps XML and reconstructs ITStudent objects
- Calculates average marks and pass/fail status
- Displays student information to console
- Deletes processed XML files
- Removes corresponding integers from buffer

#### Buffer & Synchronization

- **Buffer Size**: 10 elements (configurable)
- **Semaphores Used**:
  - `mutex`: Ensures mutual exclusion (1 semaphore)
  - `empty`: Tracks empty buffer slots (initialized to 10)
  - `full`: Tracks full buffer slots (initialized to 0)
- **Rules Enforced**:
  - Producer waits when buffer is full
  - Consumer waits when buffer is empty
  - Only one thread accesses buffer at a time

### Part 2: GitHub [10 Marks]

- Version control setup with Git
- Source code and documentation stored in repository
- Collaborative development environment
- **Repository URL**: [Your GitHub URL]
- **Team Member Profiles**:
  - [siko13-bot](https://github.com/siko13-bot)
  - [simangafakudze](https://github.com/202003666)

### Part 3: Socket Programming [20 Marks]

#### Architecture

- **Buffer Server**: Central server managing the queue
- **Producer Client**: Connects to buffer server to produce data
- **Consumer Client**: Connects to buffer server to consume data
- **Communication**: JSON-based message protocol over TCP sockets

#### Socket Features

- Multi-client support with threading
- Request-response protocol
- Commands: PRODUCE, CONSUME, STATUS
- Error handling and retry logic
- Network-based synchronization

---

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- No external libraries required (uses standard library only)

### Installation Steps

1. **Clone the repository**:

```bash
git clone [your-github-url]
cd producer-consumer-project
```

2. **Verify Python installation**:

```bash
python --version
```

3. **No additional packages needed** - uses Python standard library

---

## Usage Instructions

### Running the Multi-threaded Version

```bash
python producer_consumer.py
```

**Expected Output**:

- Producer thread generates and saves 10 XML files
- Consumer thread reads, processes, and displays student information
- Real-time buffer status updates
- Synchronized operations with no race conditions

### Running the Socket-based Version

```bash
python socket_producer_consumer.py
```

**Expected Output**:

- Buffer server starts on localhost:5000
- Producer and consumer clients connect to server
- Distributed processing of student records
- Network-based synchronization

### Example Output

```
============================================================
PRODUCER-CONSUMER PROBLEM SIMULATION
Buffer Size: 10
Students to Process: 10
============================================================

[PRODUCER] Started
[CONSUMER] Started
[PRODUCER] Produced: student1.xml (Buffer size: 1)
[CONSUMER] Consuming: student1.xml (Buffer size: 0)

============================================================
Student Name: Sipho Dlamini
Student ID: 12345678
Programme: BSc Computer Science

Courses and Marks:
------------------------------------------------------------
  Programming I                   85
  Data Structures                 78
  Web Development                 92
  Database Systems                88
  Computer Networks               76
------------------------------------------------------------
Average Mark: 83.80
Status: PASS
============================================================
```

---

## Technical Implementation Details

### Synchronization Mechanism

The project implements the classic semaphore-based solution:

```python
# Producer pseudocode
empty.acquire()      # Wait for empty slot
mutex.acquire()      # Enter critical section
# ... produce item ...
mutex.release()      # Exit critical section
full.release()       # Signal item available

# Consumer pseudocode
full.acquire()       # Wait for item
mutex.acquire()      # Enter critical section
# ... consume item ...
mutex.release()      # Exit critical section
empty.release()      # Signal slot available
```

### XML Format

Example student XML structure:

```xml
<?xml version="1.0" ?>
<student>
  <name>Sipho Dlamini</name>
  <student_id>12345678</student_id>
  <programme>BSc Computer Science</programme>
  <courses>
    <course>
      <course_name>Programming I</course_name>
      <mark>85</mark>
    </course>
    <!-- More courses... -->
  </courses>
</student>
```

### Socket Protocol

**PRODUCE Request**:

```json
{
  "command": "PRODUCE",
  "file_number": 1,
  "xml_data": "<?xml version='1.0'?>..."
}
```

**CONSUME Request**:

```json
{
  "command": "CONSUME"
}
```

**Response Format**:

```json
{
  "status": "SUCCESS|FULL|EMPTY|ERROR",
  "message": "Description",
  "buffer_size": 5
}
```

---

## Testing & Verification

### Test Scenarios

1. ✅ **Buffer Full**: Producer waits when buffer reaches capacity
2. ✅ **Buffer Empty**: Consumer waits when no items available
3. ✅ **Mutual Exclusion**: No race conditions or data corruption
4. ✅ **XML Serialization**: Data correctly wrapped and unwrapped
5. ✅ **File Operations**: XML files created and deleted properly
6. ✅ **Calculations**: Average marks and pass/fail correctly computed
7. ✅ **Socket Communication**: Network-based coordination works correctly

---

## Key Design Decisions

1. **Threading vs Multiprocessing**: Used threading for lightweight concurrency
2. **Semaphores**: Implemented standard counting semaphores for synchronization
3. **XML Library**: Used `xml.etree.ElementTree` for portability
4. **File Management**: Automatic cleanup of XML files after consumption
5. **Error Handling**: Comprehensive try-catch blocks for robustness
6. **Configurability**: Buffer size and student count easily adjustable

---

## Challenges & Solutions

### Challenge 1: Race Conditions

**Solution**: Implemented mutex semaphore for critical section protection

### Challenge 2: Deadlock Prevention

**Solution**: Proper semaphore ordering (empty→mutex→full for producer)

### Challenge 3: Socket Timeout Handling

**Solution**: Implemented retry logic with exponential backoff

### Challenge 4: XML Parsing Errors

**Solution**: Added validation and error handling in from_xml method

---

## Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Web-based monitoring dashboard
- [ ] Multi-producer, multi-consumer support
- [ ] Priority queue implementation
- [ ] Distributed buffer across multiple servers
- [ ] Performance metrics and logging
- [ ] Configuration file for parameters

---

## References

1. Operating System Concepts (Silberschatz, Galvin, Gagne)
2. Python Threading Documentation: https://docs.python.org/3/library/threading.html
3. Python Socket Programming: https://docs.python.org/3/library/socket.html
4. XML Processing in Python: https://docs.python.org/3/library/xml.etree.elementtree.html

---

## License

This project is submitted as part of CSC411 coursework at the University of Eswatini.

---

## Contact Information

For questions or issues, please contact:

- [Your Email]
- [Partner Email]

**Submission Date**: November 23, 2025
