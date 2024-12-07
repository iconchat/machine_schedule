from datetime import datetime, timedelta
import pandas as pd


# Maschinen: Enthält Details über Maschinen wie ihre Operationen, Produktionszeit pro Einheit, Kosten pro Einheit, Geschwindigkeit, Wartungsintervalle und Ausfallrate.
# Materialien: Informationen über die verfügbaren Materialien, einschließlich Lieferzeit, Mindestlagerbestand, Bufferzeit und verfügbarer Menge.
# Jobs: Enthält die Jobs, die durchgeführt werden müssen, mit Priorität, Start- und Endzeit, benötigten Operationen, Material und Anzahl der Einheiten.
# Zeitrahmen-Vorlieben: Enthält Gewichtungen für Zeit und Kosten für bestimmte Zeiträume (nicht im Algorithmus genutzt, aber vorbereitet).

# Input Data
machines = [
    {"Machine": "M1", "Operation": "Op1", "Time_Per_Unit": 10, "Cost_Per_Unit": 50, "Input_Speed": 5, "Maintenance": 2, "Failure_Rate": 5},
    {"Machine": "M2", "Operation": "Op2", "Time_Per_Unit": 15, "Cost_Per_Unit": 70, "Input_Speed": 10, "Maintenance": 1, "Failure_Rate": 2},
    {"Machine": "M3", "Operation": "Op3", "Time_Per_Unit": 20, "Cost_Per_Unit": 100, "Input_Speed": 7, "Maintenance": 1.5, "Failure_Rate": 8},
]

materials = [
    {"Material": "Steel", "Delivery_Time": 2, "Buffer": 10, "Min_Storage": 1, "Available_Quantity": 100},
    {"Material": "Aluminum", "Delivery_Time": 3, "Buffer": 20, "Min_Storage": 2, "Available_Quantity": 200},
    {"Material": "Plastic", "Delivery_Time": 1, "Buffer": 15, "Min_Storage": 1, "Available_Quantity": 150},
]

jobs = [
    {"Job": "J1", "Priority": "High", "Start": "2024-12-10 08:00", "Deadline": "2024-12-20 17:00", "Operations": ["Op1", "Op2"], "Material": "Steel", "Units": 10},
    {"Job": "J2", "Priority": "Medium", "Start": "2024-12-12 08:00", "Deadline": "2024-12-25 17:00", "Operations": ["Op2", "Op3"], "Material": "Aluminum", "Units": 15},
    {"Job": "J3", "Priority": "Low", "Start": "2024-12-15 08:00", "Deadline": "2024-12-30 17:00", "Operations": ["Op1", "Op3"], "Material": "Plastic", "Units": 20},
]

timeframe_preferences = [
    {"StartTime": "2024-12-10 08:00", "EndTime": "2024-12-20 17:00", "TimeWeight": 0.7, "CostWeight": 0.3},
    {"StartTime": "2024-12-20 08:00", "EndTime": "2024-12-25 17:00", "TimeWeight": 0.5, "CostWeight": 0.5},
    {"StartTime": "2024-12-25 08:00", "EndTime": "2024-12-30 17:00", "TimeWeight": 0.8, "CostWeight": 0.2},
]

# Scheduling Algorithm
def schedule_jobs(jobs, machines, materials):
    # Priorität wird in Zahlen übersetzt, damit die Jobs in der Reihenfolge "High", "Medium", "Low" sortiert werden.
    # Deadline dient als sekundäres Kriterium für die Sortierung.
    priority_map = {"High": 1, "Medium": 2, "Low": 3}
    jobs = sorted(jobs, key=lambda x: (priority_map[x["Priority"]], x["Deadline"]))

    # Initialize variables
    schedule = []
    machine_availability = {m["Machine"]: datetime.strptime("2024-12-10 08:00", "%Y-%m-%d %H:%M") for m in machines}
    machine_runtime = {m["Machine"]: 0 for m in machines}  # Track runtime for maintenance
    material_availability = {m["Material"]: datetime.strptime("2024-12-10 08:00", "%Y-%m-%d %H:%M") for m in materials}

    for job in jobs:
        material = next((m for m in materials if m["Material"] == job["Material"]), None)
        if not material:
            raise ValueError(f"No material found for job {job['Job']}")

        # Check material availability
        material_ready_time = material_availability[material["Material"]] + timedelta(days=material["Delivery_Time"] + material["Min_Storage"])
        job_start_time = max(material_ready_time, datetime.strptime(job["Start"], "%Y-%m-%d %H:%M"))

        for operation in job["Operations"]:
            machine = next((m for m in machines if m["Operation"] == operation), None)
            if not machine:
                raise ValueError(f"No machine found for operation {operation}")

            # Calculate operation time based on input speed
            units = job["Units"]
            time_required = (units / machine["Input_Speed"]) * 60  # Convert hours to minutes

            # Add maintenance time if needed
            if machine_runtime[machine["Machine"]] >= machine["Maintenance"] * 60:
                maintenance_time = timedelta(hours=machine["Maintenance"])
                start_time = max(job_start_time, machine_availability[machine["Machine"]] + maintenance_time)
                machine_runtime[machine["Machine"]] = 0  # Reset runtime after maintenance
            else:
                start_time = max(job_start_time, machine_availability[machine["Machine"]])

            end_time = start_time + timedelta(minutes=time_required)

            # Update material availability
            material["Available_Quantity"] -= units
            if material["Available_Quantity"] < 0:
                raise ValueError(f"Not enough material {material['Material']} for job {job['Job']}")

            # Append to schedule
            schedule.append({
                "Job": job["Job"],
                "Machine": machine["Machine"],
                "Operation": operation,
                "Units": units,
                "Start Time": start_time.strftime("%Y-%m-%d %H:%M"),
                "End Time": end_time.strftime("%Y-%m-%d %H:%M"),
                "Cost": units * machine["Cost_Per_Unit"],
            })

            # Update machine usage and runtime
            machine_availability[machine["Machine"]] = end_time
            machine_runtime[machine["Machine"]] += time_required

    return schedule

# Run the scheduler
schedule = schedule_jobs(jobs, machines, materials)

# Display the schedule
df = pd.DataFrame(schedule)
print(df.to_string(index=False))