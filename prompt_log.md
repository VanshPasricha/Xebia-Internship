# Project Prompt Log: Smart Attendance System

1. **User**: "Design a smart attendance system using Python and PyQt6 that can capture student faces and register them into a local SQLite database."
   - **Action**: Created the base project structure, set up `setup_database.py` with the student schema, and implemented the `register_student.py` GUI along with OpenCV-based face capturing functionality.

2. **User**: "Create a faculty dashboard to select classes from a timetable and start attendance sessions."
   - **Action**: Designed the timetable schema and `faculty_dashboard.py` interface. Connected it to the database so faculty members can view their scheduled classes and initiate a session for a specific day and time.

3. **User**: "Implement the face recognition engine to mark attendance automatically in real-time, preventing any duplicate entries for the same session."
   - **Action**: Developed the `face_recognizer.py` engine to compare live camera feeds against registered face embeddings. Integrated duplicate-check logic in `attendance_service.py` to ensure robust attendance marking.

4. **User**: "Add an analytics page for students to view their attendance percentage and a feature for faculty to export attendance records to a CSV file."
   - **Action**: Built the `student_dashboard.py` providing a read-only view of their timetable and attendance metrics. Added an 'Export to CSV' button in the faculty view utilizing pandas for quick report generation.

5. **User**: "Organize the project, add a README, create a folder for screenshots, and push the initial version to my GitHub repository."
   - **Action**: Finalized the `README.md`, set up the `screenshots` directory, created `.gitignore`, initialized the git repository, and pushed the entire source code to the remote repository on GitHub.
