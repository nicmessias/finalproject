import json
import datetime
import os
from typing import Dict, Any, Optional

# Data file
DATA_FILE = "wellness_data.json"

def load_data(filename: str = DATA_FILE) -> Dict:
    """Load wellness data from JSON file. Returns default structure if file doesn't exist."""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not read data file. Starting fresh.")
    # Default structure
    return {
        "goals": {
            "water": 8,      # glasses per day
            "exercise": 30,  # minutes per day
            "vitamins": True,
            "sleep": 8       # hours
        },
        "logs": {}  # date -> category data
    }

def save_data(data: Dict, filename: str = DATA_FILE) -> None:
    """Save current data to JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        print("Error: Could not save data.")

def log_entry(category: str, value: Any, date: Optional[str] = None, notes: str = "", filename: str = DATA_FILE) -> bool:
    """Log an entry for a wellness category. Returns True if successful."""
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
    """Return summary for a specific day or today."""
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
    """Check goal completion for a day and return stats."""
    # FIXED: Passed filename parameter downstream
    summary = get_daily_summary(date, filename)
    if "status" in summary:
        return {"date": summary["date"], "completion_rate": 0, "completed": []}
    
    total = len(summary["categories"])
    completed = sum(1 for cat in summary["categories"].values() if cat["completed"])
    
    return {
        "date": summary["date"],
        "completion_rate": round((completed / total) * 100, 1) if total else 0,
        "completed_count": completed,
        "total_goals": total
    }

def generate_weekly_report(filename: str = DATA_FILE) -> Dict:
    """Generate a weekly summary with averages and streaks."""
    data = load_data(filename)
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    
    daily_rates = []
    streak = 0
    current_streak = 0
    
    for i in range(7):
        check_date = (today - datetime.timedelta(days=i)).isoformat()
        # FIXED: Passed filename parameter downstream
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
        "daily_rates": daily_rates[::-1]  # most recent first
    }

def main():
    """Main program loop with menu."""
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
            summary = get_daily_summary()
            print("\nToday's Summary:")
            print(json.dumps(summary, indent=2))
        elif choice == "3":
            result = check_goals()
            print(f"\nGoal completion for today: {result['completion_rate']}%")
        elif choice == "4":
            report = generate_weekly_report()
            print("\nWeekly Report:")
            print(f"Period: {report['period']}")
            print(f"Average completion rate: {report['average_completion']}%")
            print(f"Longest streak: {report['longest_streak']} days")
        elif choice == "5":
            set_goals()
        elif choice == "6":
            print("Goodbye! Stay healthy!")
            break
        else:
            print("Invalid choice. Please try again.")

def log_today():
    """Helper for logging multiple categories today."""
    categories = ["water", "exercise", "vitamins", "sleep"]
    print("\nLog today's activities:")
    
    for cat in categories:
        if cat == "vitamins":
            val = input(f"Did you take your vitamins? (y/n): ").strip().lower()
            value = val in ["y", "yes"]
        else:
            while True:
                try:
                    prompt = f"Enter {cat} value ({'glasses' if cat=='water' else 'minutes' if cat=='exercise' else 'hours'}): "
                    value = float(input(prompt))
                    break
                except ValueError:
                    print("Please enter a valid number.")
        notes = input(f"Notes for {cat} (optional): ").strip()
        log_entry(cat, value, notes=notes)
        print(f"Logged {cat} successfully.")

def set_goals():
    """Update user goals."""
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

if __name__ == "__main__":
    main()