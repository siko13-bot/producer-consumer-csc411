import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

class ITStudent:
    """Class representing an IT student with their academic information."""
    
    # Sample data for random generation
    FIRST_NAMES = ["Sipho", "Thandi", "Bongani", "Nomsa", "Mandla", "Zanele", 
                   "Sifiso", "Precious", "Lungelo", "Nokuthula"]
    LAST_NAMES = ["Dlamini", "Nkosi", "Mamba", "Simelane", "Mnisi", "Zwane",
                  "Shongwe", "Magagula", "Fakudze", "Ndlovu"]
    PROGRAMMES = ["BSc Computer Science", "BSc Information Technology", 
                  "BSc Software Engineering", "BSc Data Science"]
    COURSES = ["Programming I", "Data Structures", "Database Systems", 
               "Web Development", "Computer Networks", "Software Engineering",
               "Operating Systems", "Artificial Intelligence"]
    
    def __init__(self):
        """Initialize student with randomly generated data."""
        self.student_name = self._generate_name()
        self.student_id = self._generate_student_id()
        self.programme = random.choice(self.PROGRAMMES)
        self.courses = self._generate_courses()
    
    def _generate_name(self):
        """Generate a random student name."""
        first = random.choice(self.FIRST_NAMES)
        last = random.choice(self.LAST_NAMES)
        return f"{first} {last}"
    
    def _generate_student_id(self):
        """Generate a random 8-digit student ID."""
        return str(random.randint(10000000, 99999999))
    
    def _generate_courses(self):
        """Generate a list of 4-6 courses with random marks."""
        num_courses = random.randint(4, 6)
        selected_courses = random.sample(self.COURSES, num_courses)
        return {course: random.randint(30, 100) for course in selected_courses}
    
    def to_xml(self):
        """Convert student information to XML format."""
        root = ET.Element("student")
        
        name_elem = ET.SubElement(root, "name")
        name_elem.text = self.student_name
        
        id_elem = ET.SubElement(root, "student_id")
        id_elem.text = self.student_id
        
        programme_elem = ET.SubElement(root, "programme")
        programme_elem.text = self.programme
        
        courses_elem = ET.SubElement(root, "courses")
        for course_name, mark in self.courses.items():
            course_elem = ET.SubElement(courses_elem, "course")
            course_name_elem = ET.SubElement(course_elem, "course_name")
            course_name_elem.text = course_name
            mark_elem = ET.SubElement(course_elem, "mark")
            mark_elem.text = str(mark)
        
        # Pretty print the XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        return xml_str
    
    @classmethod
    def from_xml(cls, xml_string):
        """Create an ITStudent object from XML string."""
        root = ET.fromstring(xml_string)
        
        student = cls.__new__(cls)
        student.student_name = root.find("name").text
        student.student_id = root.find("student_id").text
        student.programme = root.find("programme").text
        
        student.courses = {}
        courses_elem = root.find("courses")
        for course in courses_elem.findall("course"):
            course_name = course.find("course_name").text
            mark = int(course.find("mark").text)
            student.courses[course_name] = mark
        
        return student
    
    def calculate_average(self):
        """Calculate the average mark across all courses."""
        if not self.courses:
            return 0
        return sum(self.courses.values()) / len(self.courses)
    
    def determine_pass_fail(self):
        """Determine if the student passed (average >= 50%)."""
        return "PASS" if self.calculate_average() >= 50 else "FAIL"
    
    def display_info(self):
        """Display student information in a formatted way."""
        print("\n" + "="*60)
        print(f"Student Name: {self.student_name}")
        print(f"Student ID: {self.student_id}")
        print(f"Programme: {self.programme}")
        print("\nCourses and Marks:")
        print("-" * 60)
        for course, mark in self.courses.items():
            print(f"  {course:<30} {mark:>3}")
        print("-" * 60)
        avg = self.calculate_average()
        status = self.determine_pass_fail()
        print(f"Average Mark: {avg:.2f}")
        print(f"Status: {status}")
        print("="*60 + "\n")