class Employee:
    def __init__(self, name, employee_id, hourly_rate):
        self.name = name
        self.employee_id = employee_id
        self.hourly_rate = hourly_rate
    
    def calculate_weekly_pay(self, hours_worked):
        raise NotImplementedError("Subclasses should implement this!")
    
    def get_details(self):
        return f"Name: {self.name}, Employee ID: {self.employee_id}, Hourly Rate: ${self.hourly_rate:.2f}"


class FullTimeEmployee(Employee):
    def calculate_weekly_pay(self, hours_worked):
        # Full-time assumes 40 hours regardless of hours_worked passed
        return self.hourly_rate * 40
    
    def get_details(self):
        base_details = super().get_details()
        return f"{base_details} (Full-Time)"


class PartTimeEmployee(Employee):
    def calculate_weekly_pay(self, hours_worked):
        return self.hourly_rate * hours_worked
    
    def get_details(self):
        base_details = super().get_details()
        return f"{base_details} (Part-Time)"


# Main program
if __name__ == "__main__":
    # Create Full-Time Employees
    ft1 = FullTimeEmployee("Alice Johnson", "FT001", 28.50)
    ft2 = FullTimeEmployee("Bob Smith", "FT002", 32.75)
    
    # Create Part-Time Employees
    pt1 = PartTimeEmployee("Carol Davis", "PT001", 22.00)
    pt2 = PartTimeEmployee("David Wilson", "PT002", 19.75)
    
    # Define hours worked (full-time will use 40 internally)
    hours_ft1 = 40
    hours_ft2 = 40
    hours_pt1 = 25
    hours_pt2 = 18
    
    # Print details and weekly pay for each
    employees = [
        (ft1, hours_ft1),
        (ft2, hours_ft2),
        (pt1, hours_pt1),
        (pt2, hours_pt2)
    ]
    
    print("Employee Payroll Report\n")
    for emp, hours in employees:
        print(emp.get_details())
        pay = emp.calculate_weekly_pay(hours)
        print(f"Weekly Pay: ${pay:.2f}\n")
