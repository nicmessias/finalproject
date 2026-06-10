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
    """Save current data state safely to a target JSON database configuration."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        print("Error: Could not save data.")

def log_entry(category: str, value: Any, date: Optional[str] = None, notes: str = "", filename: str = DATA_FILE) -> bool:
    """Log an entry for a specific metrics category on a targeted database ledger date."""
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
    """Evaluate metric accomplishments by cross-checking goals vs actual inputs."""
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
    """Calculate specific targeted metrics rates across custom logged inputs."""
    summary = get_daily_summary(date, filename)
    if "status" in summary:
        return {"date": summary["date"], "completion_rate": 0, "completed_count": 0, "total_goals": 4}
    
    total = len(summary["categories"])
    completed = sum(1 for cat in summary["categories"].values() if cat["completed"])
    
    return {
        "date": summary["date"],
        "completion_rate": round((completed / total) * 100, 1) if total else 0,
        "completed_count": completed,
        "total_goals": total
    }

def generate_weekly_report(filename: str = DATA_FILE) -> Dict:
    """Read data back spanning multiple days to evaluate macro trends and streaks."""
    data = load_data(filename)
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    
    daily_rates = []
    streak = 0
    current_streak = 0
    
    for i in range(7):
        check_date = (today - datetime.timedelta(days=i)).isoformat()
        result = check_goals(check_date, filename)
        daily_rates.append(result["completion_rate"])
        
        if result["completion_rate"] >= 80:
            current_streak += 1
        else:
            if current_streak > streak:
                streak = current_streak
            current_streak = 0
    
    if current_streak > streak:
        streak = current_streak
    
    avg_rate = round(sum(daily_rates) / len(daily_rates), 1) if daily_rates else 0
    
    return {
        "period": f"{week_ago} to {today}",
        "average_completion": avg_rate,
        "longest_streak": streak,
        "daily_rates": daily_rates[::-1]  # formatted chronologically
    }

def log_today():
    """Menu Helper: Prompt input records sequentially across multiple wellness buckets."""
    categories = ["water", "exercise", "vitamins", "sleep"]
    print("\nLog today's activities:")
    
    for cat in categories:
        if cat == "vitamins":
            val = input("Did you take your vitamins? (y/n): ").strip().lower()
            value = val in ["y", "yes"]
        else:
            while True:
                try:
                    units = 'glasses' if cat == 'water' else 'minutes' if cat == 'exercise' else 'hours'
                    prompt = f"Enter {cat} value ({units}): "
                    value = float(input(prompt))
                    break
                except ValueError:
                    print("Please enter a valid number.")
        notes = input(f"Notes for {cat} (optional): ").strip()
        log_entry(cat, value, notes=notes)
        print(f"Logged {cat} successfully.")

def set_goals():
    """Menu Helper: Modify active configuration validation thresholds dynamically."""
    data = load_data()
    print("\nCurrent goals:", data["goals"])
    
    for key in data["goals"]:
        if key == "vitamins":
            new_val = input(f"Take vitamins daily? (y/n) [current: {data['goals'][key]}]: ").strip().lower()
            data["goals"][key] = new_val in ["y", "yes"]
        else:
            try:
                new_val = float(input(f"New goal for {key}: "))
                data["goals"][key] = new_val
            except ValueError:
                print("Keeping current value.")
    save_data(data)
    print("Goals updated!")

def main():
    """Application Loop Control Hub interface execution engine logic matrix."""
    print("=== Wellness Tracker ===")
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
            # Call daily summary helper
            summary = get_daily_summary()
            print("\nToday's Summary:")
            
            # FIXED: Catching if no metrics have been recorded for today yet
            if "status" in summary:
                print(f"-> {summary['status']}. Please use Option 1 to record metrics first!")
            else:
                print(json.dumps(summary, indent=2))
                
        elif choice == "3":
            # Fetch goal statistical rates
            result = check_goals()
            
            # FIXED: Print a clear fallback if completion count shows 0 entries 
            if result.get("completed_count", 0) == 0 and result.get("completion_rate") == 0:
                print(f"\nGoal completion for today: {result['completion_rate']}%")
                print("-> Notice: No completed targets recorded for today's date yet.")
            else:
                print(f"\nGoal completion for today: {result['completion_rate']}%")
                print(f"Progress: {result['completed_count']} out of {result['total_goals']} goals met!")
                
        elif choice == "4":
            print("\nAnalyzing past 7 days of logs...")
            report = generate_weekly_report()
            
            # FIXED: Display the calculated analytical moving arrays properly
            print("\n=== Weekly Report ===")
            print(f"Period: {report['period']}")
            print(f"Average completion rate: {report['average_completion']}%")
            print(f"Longest streak: {report['longest_streak']} days")
            print(f"Daily historical trend (past 7 days): {report['daily_rates']}")
        elif choice == "5":
            set_goals()
        elif choice == "6":
            print("Goodbye! Stay healthy!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()