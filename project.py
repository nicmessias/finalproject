"""
BeHeathy Tracker Application
----------------------------
Author: Emiliano Acero and Nicole Messias 
GitHub Username: eaceroyee1308 and nicmessias
Date: June 16, 2026

Academic Integrity Citation:
This project was developed with the assistance of an AI collaborator (Gemini)
to refine data pipeline architectures, troubleshoot file-locking testing fixtures,
and ensure structural validation against requirements.
"""

import json
import datetime
import os
from typing import Dict, Any, Optional

# Data file path
DATA_FILE = "wellness_data.json"


def load_data(filename: str = DATA_FILE) -> Dict:
    """Load wellness data from JSON file. Returns default structure if file doesn't exist."""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not read data file. Starting fresh.")
    
    # Default fallback data structure
    return {
        "goals": {
            "water": 8,      # glasses per day
            "exercise": 30,  # minutes per day
            "vitamins": True,
            "sleep": 8       # hours
        },
        "logs": {}  # maps date string -> logged category tracking data
    }


def save_data(data: Dict, filename: str = DATA_FILE) -> None:
    """Save current data state to JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        print("Error: Could not save data.")


def log_entry(category: str, value: Any, date: Optional[str] = None, 
              notes: str = "", filename: str = DATA_FILE) -> bool:
    """Log an entry for a specific category."""
    data = load_data(filename)
    
    if date is None:
        date = datetime.date.today().isoformat()
    
    if date not in data["logs"]:
        data["logs"][date] = {}
    
    data["logs"][date][category] = {
        "value": value,
        "notes": notes,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    save_data(data, filename)
    return True


def get_daily_summary(date: Optional[str] = None, filename: str = DATA_FILE) -> Dict:
    """Get summary of daily progress vs goals."""
    if date is None:
        date = datetime.date.today().isoformat()
    
    data = load_data(filename)
    if date not in data["logs"]:
        return {"date": date, "status": "No data logged yet"}
    
    logs = data["logs"][date]
    goals = data["goals"]
    
    summary = {"date": date, "categories": {}}
    
    for cat, goal in goals.items():
        if cat in logs:
            value = logs[cat]["value"]
            if cat == "vitamins":
                completed = bool(value)
            else:
                completed = value >= goal
            summary["categories"][cat] = {
                "logged": value,
                "goal": goal,
                "completed": completed
            }
        else:
            summary["categories"][cat] = {
                "logged": 0,
                "goal": goal,
                "completed": False
            }
    return summary


def check_goals(date: Optional[str] = None, filename: str = DATA_FILE) -> Dict:
    """Calculate goal completion rate for a given date."""
    summary = get_daily_summary(date, filename)
    if "status" in summary:
        return {
            "date": summary["date"],
            "completion_rate": 0.0,
            "completed_count": 0,
            "total_goals": 4
        }
    
    total = len(summary["categories"])
    completed = sum(1 for cat in summary["categories"].values() if cat["completed"])
    
    return {
        "date": summary["date"],
        "completion_rate": round((completed / total) * 100, 1) if total else 0.0,
        "completed_count": completed,
        "total_goals": total
    }


def generate_weekly_report(filename: str = DATA_FILE) -> Dict:
    """Generate weekly report with average completion and longest streak."""
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    
    daily_rates = []
    longest_streak = 0
    current_streak = 0
    
    for i in range(7):
        check_date = (today - datetime.timedelta(days=i)).isoformat()
        result = check_goals(check_date, filename)
        rate = result["completion_rate"]
        daily_rates.append(rate)
        
        if rate >= 80:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0
    
    avg_rate = round(sum(daily_rates) / len(daily_rates), 1) if daily_rates else 0.0
    
    # Show dates from oldest to newest
    daily_rates_chrono = daily_rates[::-1]
    
    return {
        "period": f"{week_ago.isoformat()} to {today.isoformat()}",
        "average_completion": avg_rate,
        "longest_streak": longest_streak,
        "daily_rates": daily_rates_chrono
    }


def log_today():
    """Log activities for today."""
    categories = ["water", "exercise", "vitamins", "sleep"]
    print("\n=== Log Today's Activities ===")
    
    for cat in categories:
        if cat == "vitamins":
            val = input("Did you take your vitamins? (y/n): ").strip().lower()
            value = val in ["y", "yes", "1", "true"]
        else:
            while True:
                try:
                    units = 'glasses' if cat == 'water' else 'minutes' if cat == 'exercise' else 'hours'
                    prompt = f"Enter {cat} ({units}): "
                    value = float(input(prompt))
                    if value < 0:
                        print("Value cannot be negative. Try again.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        notes = input(f"Notes for {cat} (optional): ").strip()
        log_entry(cat, value, notes=notes)
        print(f"✅ Logged {cat} successfully.\n")


def set_goals():
    """Update daily goals."""
    data = load_data()
    print("\n=== Current Goals ===")
    for k, v in data["goals"].items():
        print(f"  {k.capitalize()}: {v}")
    
    print("\nEnter new goals (press Enter to keep current value):")
    
    for key in list(data["goals"].keys()):
        if key == "vitamins":
            new_val = input(f"Take vitamins daily? (y/n) [current: {data['goals'][key]}]: ").strip().lower()
            if new_val:
                data["goals"][key] = new_val in ["y", "yes", "1", "true"]
        else:
            while True:
                try:
                    current = data["goals"][key]
                    prompt = f"New goal for {key} (current: {current}): "
                    new_input = input(prompt).strip()
                    if new_input == "":
                        break  # keep current
                    new_val = float(new_input)
                    if new_val < 0:
                        print("Goal cannot be negative.")
                        continue
                    data["goals"][key] = new_val
                    break
                except ValueError:
                    print("Please enter a valid number or press Enter to skip.")
    
    save_data(data)
    print("✅ Goals updated successfully!")


def main():
    """Main application loop."""
    print("=== BeHealthy Wellness Tracker ===")
    print("Your personal daily health companion\n")
    
    while True:
        print("\nMain Menu:")
        print("1. Log today's activities")
        print("2. View today's summary")
        print("3. Check goals")
        print("4. Generate weekly report")
        print("5. Set new goals")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            log_today()
            
        elif choice == "2":
            summary = get_daily_summary()
            print("\n=== Today's Summary ===")
            if "status" in summary:
                print(f"→ {summary['status']}")
                print("   Please use Option 1 to log your activities first!")
            else:
                print(f"Date: {summary['date']}\n")
                for cat, info in summary["categories"].items():
                    status = "✅ Completed" if info["completed"] else "❌ Not met"
                    goal_display = "Yes/No" if cat == "vitamins" else str(info['goal'])
                    logged_display = "Yes" if (cat == "vitamins" and info["logged"]) else ("No" if cat == "vitamins" else str(info["logged"]))
                    print(f"  {cat.capitalize():10} : {logged_display:>5} / {goal_display:<6} → {status}")
                    
        elif choice == "3":
            result = check_goals()
            print(f"\n=== Goal Completion for Today ===")
            print(f"Completion Rate : {result['completion_rate']}%")
            print(f"Progress        : {result['completed_count']} / {result['total_goals']} goals met")
            if result['completed_count'] == 0:
                print("→ No goals completed yet today.")
                
        elif choice == "4":
            print("\nAnalyzing past 7 days...")
            report = generate_weekly_report()
            print("\n=== Weekly Report ===")
            print(f"Period               : {report['period']}")
            print(f"Average Completion   : {report['average_completion']}%")
            print(f"Longest Streak       : {report['longest_streak']} days")
            print(f"Daily Rates (oldest→newest): {report['daily_rates']}")
            
        elif choice == "5":
            set_goals()
            
        elif choice == "6":
            print("Goodbye! Stay healthy! 💪")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()