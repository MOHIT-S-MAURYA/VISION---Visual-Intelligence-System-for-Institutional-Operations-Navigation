# Quick Start Guide: Subject Management System

## What Changed?

Subjects are now stored in the database instead of a JavaScript file. Teachers can now add, edit, and delete subjects through the web interface!

## How to Use

### 1. Managing Subjects (Teachers)

1. **Access the Subjects Page**

   - Click "Subjects" in the navigation menu
   - You'll see the Subjects Management page

2. **View Subjects**

   - Select a Department from the dropdown (e.g., "CSE")
   - Select a Year (e.g., "Second Year")
   - All subjects for that combination will appear in the table

3. **Add a New Subject**

   - Click the "Add Subject" button
   - Fill in the form:
     - Department: Choose the department
     - Year: Choose the year
     - Subject Name: Enter the subject name (e.g., "Data Structures")
     - Subject Code: (Optional) Enter a code (e.g., "CS201")
   - Click "Save"

4. **Edit a Subject**

   - Find the subject in the table
   - Click the ✏️ (edit) icon
   - Modify the details in the form
   - Click "Save"

5. **Delete a Subject**
   - Find the subject in the table
   - Click the 🗑️ (delete) icon
   - Confirm the deletion

### 2. Using Subjects in Attendance

1. **Go to Attendance Page**

   - Click "Attendance" in the navigation

2. **Create a Session**
   - Select Department (e.g., "CSE")
   - Select Class/Year (e.g., "Second Year")
   - The Subject dropdown will automatically load subjects from the database
   - Only subjects you've added in the Subjects Management page will appear
   - Select the subject and continue as usual

## Current Database Status

### Subjects Already Available

**CSE (Computer Science Engineering) - 32 subjects**

- First Year: 8 subjects
- Second Year: 8 subjects
- Third Year: 8 subjects
- Fourth Year: 8 subjects

**MCA (Master of Computer Applications) - 16 subjects**

- First Year: 8 subjects
- Second Year: 8 subjects

### Adding Subjects for Other Departments

For the remaining 24 departments, you need to add subjects using the Subjects Management page:

**UG Programs** (Need subjects for Years 1-4):

- ECE, EEE, MECH, CIVIL, IT, AI, AIDS, AIML, CSBS, CSE-Cyber, CSE-IoT, ETE, BME, AUTO, CHEM, META

**PG Programs** (Need subjects for Years 1-2):

- M.Tech CSE, M.Tech ECE, M.Tech VLSI, M.Tech Power Systems, M.Tech Structural, M.Tech Thermal, M.Tech Machine Design, M.Tech Environmental, M.Tech Production

## Tips

1. **Organize Your Subjects**

   - Add all First Year subjects for a department first
   - Then move to Second Year, and so on
   - This makes it easier to manage

2. **Use Consistent Naming**

   - Keep subject names consistent across departments
   - For example, all departments might have "Engineering Mathematics-I" in First Year

3. **Subject Codes**

   - Subject codes are optional but helpful for identification
   - Use your institution's official subject codes if available

4. **Backup Your Data**
   - Subjects are stored in the database
   - The database file is at `backend/db.sqlite3`
   - Consider backing it up regularly

## Troubleshooting

### No subjects appear in Attendance page

- Make sure you've added subjects for that department-year combination
- Check that you selected the correct department and year
- Try refreshing the page

### Can't add a subject

- Check if a subject with the same name already exists for that department-year
- The system prevents duplicate subjects

### Delete button doesn't work

- You must confirm the deletion in the popup dialog
- If a session is using that subject, you might need to handle that first

## Technical Notes

- Subjects are stored in the `students_subject` table
- Each subject is unique per department-year-name combination
- API endpoint: `http://localhost:8000/api/subjects/`
- Frontend automatically fetches subjects when department/year changes

---

**Need Help?** Check the detailed `MIGRATION_SUMMARY.md` file for technical details.
