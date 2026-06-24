"""
Windows Auto-Run Setup
=======================
Sets up a Windows Task Scheduler task to run the job search
automatically every 6 hours (or on login).

Run this once:
    python setup_autorun.py

To remove:
    python setup_autorun.py --remove
"""

import os
import sys
import subprocess


TASK_NAME = "JobSearchAutomation"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_PATH = sys.executable
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "job_search.py")


def create_task():
    """Create a Windows Task Scheduler task."""
    print("Setting up auto-run with Windows Task Scheduler...")
    print(f"  Python:  {PYTHON_PATH}")
    print(f"  Script:  {SCRIPT_PATH}")
    print(f"  Dir:     {SCRIPT_DIR}")
    print()

    # Create XML task definition for more control
    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Automatically searches for remote internships every 6 hours</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT6H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2024-01-01T08:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
  </Settings>
  <Actions>
    <Exec>
      <Command>{PYTHON_PATH}</Command>
      <Arguments>"{SCRIPT_PATH}"</Arguments>
      <WorkingDirectory>{SCRIPT_DIR}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    # Save XML file
    xml_path = os.path.join(SCRIPT_DIR, "task_schedule.xml")
    with open(xml_path, "w", encoding="utf-16") as f:
        f.write(xml_content)

    # Register with Task Scheduler
    cmd = f'schtasks /Create /TN "{TASK_NAME}" /XML "{xml_path}" /F'

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Task created successfully!")
            print(f"   Name: {TASK_NAME}")
            print(f"   Schedule: Every 6 hours + on login")
            print()
            print("   To view: Open Task Scheduler > find 'JobSearchAutomation'")
            print("   To run now: schtasks /Run /TN \"JobSearchAutomation\"")
            print("   To remove: python setup_autorun.py --remove")
        else:
            print(f"❌ Failed to create task:")
            print(f"   {result.stderr}")
            print()
            print("   Try running this script as Administrator.")
            print("   Or manually create it:")
            print(f'   schtasks /Create /TN "{TASK_NAME}" /XML "{xml_path}" /F')
    except Exception as e:
        print(f"❌ Error: {e}")

    # Clean up XML
    if os.path.exists(xml_path):
        os.remove(xml_path)


def remove_task():
    """Remove the scheduled task."""
    print(f"Removing task '{TASK_NAME}'...")
    cmd = f'schtasks /Delete /TN "{TASK_NAME}" /F'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Task removed successfully!")
        else:
            print(f"⚠️ {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    if "--remove" in sys.argv:
        remove_task()
    else:
        create_task()


if __name__ == "__main__":
    main()
