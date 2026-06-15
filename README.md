# BeHealthy Wellness Tracker
#### Video Demo: [PASTE YOUR YOUTUBE URL HERE]
#### Description:

The **BeHealthy Wellness Tracker** is a command-line interface (CLI) personal health application designed to help users track their fundamental daily health habits, assess their behaviors relative to structured goals, and analyze historical performance trends over rolling seven-day periods. Built entirely in Python, the application runs directly in the terminal and stores all data locally, making it lightweight, private, and easy to use without any internet connection or external accounts.

Maintaining consistent health logs can be a high-friction process. Most wellness apps require account creation, internet access, or complex setup. This program addresses that friction by keeping all data localized within an easy-to-parse JSON file and exposing interactive menu prompts that guide users through daily tracking without over-complicating inputs. The goal was to build something that anyone could open in a terminal and start using within seconds.

---

### What the Application Does

BeHealthy tracks four core daily health categories: **water intake** (in glasses), **exercise duration** (in minutes), **vitamin intake** (yes or no), and **sleep duration** (in hours). For each category, users can define personal goals and log their actual daily values. The application then compares logged values against goals, calculates completion rates, and generates weekly performance summaries.

The main menu offers six options:

1. **Log today's activities** — walks the user through each health category one by one, prompting for a value and optional notes for each entry.
2. **View today's summary** — displays all four categories side by side with logged values, goal targets, and a completed or not met status for each.
3. **Check goals** — shows the overall completion rate for today as a percentage, along with a count of how many goals were met out of four.
4. **Generate weekly report** — analyzes the past seven days and returns an average completion rate, the longest streak of days where at least 80% of goals were met, and a day-by-day breakdown of completion rates from oldest to newest.
5. **Set new goals** — allows the user to update any of the four goal targets at any time, with the current value shown as a reference and the option to press Enter to keep it unchanged.
6. **Exit** — closes the application cleanly.

---

### Project File Breakdown

**`project.py`**
This is the core of the application and contains all logic from runtime orchestration to file I/O and calculations. The `main()` function runs the interactive menu loop and delegates to helper functions based on user input. The file contains six key functions beyond `main()`:

- `load_data(filename)` — reads the JSON data file and returns the parsed dictionary, or a default structure if the file does not exist or is unreadable.
- `save_data(data, filename)` — serializes the current data dictionary back to the JSON file after any change.
- `log_entry(category, value, date, notes, filename)` — writes a single tracked value to the appropriate date and category in the data file, including a timestamp and optional notes.
- `get_daily_summary(date, filename)` — builds a structured summary of logged values versus goals for a given date, marking each category as completed or not.
- `check_goals(date, filename)` — calculates the overall goal completion rate for a given date, returning the percentage, count of completed goals, and total goal count.
- `generate_weekly_report(filename)` — iterates over the past seven days, computes per-day completion rates, calculates the average across the week, and identifies the longest consecutive streak of high-performance days.

**`test_project.py`**
This is the automated validation layer for the application, built using the `pytest` framework. It contains 12 test functions that cover three core modules: `log_entry`, `get_daily_summary`, and `check_goals`. Each test creates a temporary isolated data file (`test_wellness_data.json`) before running and deletes it afterward, ensuring that real user data is never touched during testing. The tests validate logging consistency, safe failure modes when querying dates with no data, goal completion detection for both met and unmet cases, and accurate partial and full completion rate calculations.

**`requirements.txt`**
Lists the external dependencies required to run and test the application. Currently this includes `pytest`, which is used to execute the automated test suite. No other third-party libraries are required since the application relies entirely on Python's standard library for JSON handling, date operations, and file I/O.

**`wellness_data.json`**
This is the data layer of the program. It stores two top-level keys: `goals`, which holds the user's current numeric or boolean targets for each health category, and `logs`, which maps ISO-formatted date strings to dictionaries of logged entries. Each logged entry includes the recorded value, any optional notes the user added, and a timestamp of when the entry was saved. The file is created automatically on first run if it does not already exist.

---

### Design Decisions and Rationales

**1. Data Layer Strategy: JSON vs SQLite**

During the initial design phase, I considered implementing a relational database using Python's built-in `sqlite3` module. However, because the core data naturally represents a nested associative structure — mapping dates to categories to values — a relational schema would have introduced unnecessary complexity. Joins, table definitions, and schema migrations would all be required for what is essentially a key-value log. Choosing a nested JSON model allowed the use of Python's built-in `dict` and `json` tools seamlessly while keeping the data file human-readable and easily auditable. A user can open `wellness_data.json` in any text editor and immediately understand the structure of their own data.

**2. Optional Filename Parameter for Testability**

When building applications that perform continuous disk access, there is a real risk of corrupting production data during testing. To address this, every function that reads or writes data accepts an optional `filename` argument that defaults to the production file path. This design choice allowed `test_project.py` to redirect all file operations to a temporary sandbox file that is created fresh and deleted after each individual test. The result is a fully isolated test environment where no test can interfere with another or with real user data.

**3. Menu-Driven CLI Over a Web Interface**

An early design consideration was whether to build the application as a Flask-based web app. Ultimately, a CLI was chosen because it better matched the goal of a lightweight, dependency-minimal tool. A web interface would have introduced a server, HTML templates, and a browser dependency — none of which add value for a personal daily tracker. The CLI keeps the experience focused and fast, requiring only Python to run.

**4. Weekly Streak Threshold Set at 80%**

When calculating the longest streak in the weekly report, a day is counted as a streak day only if its completion rate is 80% or higher rather than requiring a perfect 100%. This threshold was a deliberate design choice to make the streak feature motivating rather than discouraging. Requiring perfect completion every day would cause a single missed vitamin to break a streak, which feels punishing for a wellness tool. An 80% threshold rewards consistent effort while still holding users to a meaningful standard.

---

### Academic Integrity

This project was developed with the assistance of AI tools (Gemini and Claude) to refine data pipeline architecture, troubleshoot file-locking testing fixtures, and ensure structural validation against project requirements. All core logic, design decisions, and written documentation reflect the original work of the authors. AI assistance is cited in the comments of `project.py` in accordance with course policy.

---

*Authors: Emiliano Acero and Nicole Messias — Hult International Business School, June 2026*