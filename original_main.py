import random
from tabulate import tabulate
import csv
import tkinter as tk
import io
import sys
import sqlite3


days = 260

salespeople = []

products = []



class PrintToTextWidget:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class Product:
    def __init__(self, name, price, base_commission_rate, add_commission_rate):
        self.name = name
        self.price = price
        self.base_commission_rate = base_commission_rate
        self.add_commission_rate = add_commission_rate




class Salesperson:
    def __init__(self, name, team, base_salary, commission_rate, skill_level, network_size, vacation_likelihood, work_ethic):
        self.name = name
        self.team = team
        self.base_salary = base_salary
        self.commission_rate = commission_rate
        self.skill_level = skill_level
        self.network_size = network_size
        self.vacation_likelihood = vacation_likelihood
        self.work_ethic = work_ethic
        self.sales = []
        self.commissions = []
        self.sales_count = []
        self.attempts = 0
        self.bonus = 0
        self.vacation_days_used = 0
        self.vacation_days_remaining = 16
        self.days_worked = 0


    def take_vacation(self):
        if self.vacation_days_remaining <= 0:
            return False

        # Determine the probability of taking a vacation based on vacation_likelihood
        vacation_probability = 1 / self.vacation_likelihood

        # Take a vacation only if a random number falls within the determined probability
        if random.random() <= vacation_probability:
            vacation_length = random.randint(1, 2)  # Vacation length in days (you can change this to weeks if needed)
            if self.vacation_days_remaining >= vacation_length:
                self.vacation_days_used += vacation_length
                self.vacation_days_remaining -= vacation_length
                return True

        return False



    def make_sale(self):
        # Determine the number of sale opportunities based on network_size
        sale_opportunities = self.network_size // 10

        for _ in range(int(sale_opportunities)):
            # Determine probability of making a sale based on skill_level (0 to 1)
            sale_probability = self.skill_level / 100

            # Increment attempts
            self.attempts += 1

            # Make a sale only if a random number falls within the determined probability
            if random.random() <= sale_probability:
                product = random.choice(products)  # Randomly select a product
                sale_amount = product.price
                self.sales.append(sale_amount)
                commission = sale_amount * (product.base_commission_rate + self.commission_rate)
                self.commissions.append(commission)


    def calculate_pay(self):
        return sum(self.commissions) + self.bonus

    def total_sales(self):
        return sum(self.sales)

    def total_sales_count(self):
        return len(self.sales)
    
    # def check_bonus(self):
    #     bonus_threshold = 500000
    #     bonus_amount = 100000
    #     if self.total_sales() > bonus_threshold:
    #         self.bonus = bonus_amount

    def check_bonus(self):
        bonus_thresholds = [2000000,1000000,500000, 250000, 100000]
        bonus_amounts = [500000,250000,100000, 2500, 500]

        self.bonus = 0
        for threshold, amount in zip(bonus_thresholds, bonus_amounts):
            if self.total_sales() > threshold:
                self.bonus = amount
                break

class SalesCompany:
    def __init__(self, salespeople, revenue, commissions, profit):
        self.salespeople = salespeople
        self.revenue = 0
        self.commissions = 0
        self.profit = 0
        self.payroll = 0
 
    def generate_sales(self, salesperson):
        salesperson.make_sale()
        if salesperson.sales:
            self.revenue += salesperson.sales[-1]

    def update_payroll(self):
        for salesperson in self.salespeople:
            self.payroll += salesperson.base_salary
        # for salesperson in self.salespeople:
        #     self.commissions += salesperson.commissions
        # self.payroll = sum(salesperson.base_salary for salesperson in self.salespeople)
        self.commissions = sum(salesperson.calculate_pay() for salesperson in self.salespeople)
 
 
    def update_profit(self):
        self.profit = self.revenue - (self.payroll + self.commissions)

# def display_results(salespeople, weeks):
#     print("\nSales Results:\n")
#     for salesperson in salespeople:
#         print(f"{salesperson.name}: ${salesperson.total_sales():,.2f} in sales, ${salesperson.calculate_pay():,.2f} total commissions, ${salesperson.base_salary * weeks:,.2f} total base pay")


def divZ(x,y):
    return x/y if y else 0



def display_leaderboard(salespeople):
    global days
    headers = ["Employees","C %","Sales","Commissions","Base Pay","Bonus","Total Comp","Sales Count","Attempts","Success %","Profit", "Vacation Days Used", "Days Worked"]
    sorted_salespeople = sorted(salespeople, key=lambda sp: sp.total_sales(), reverse=True)
    table = []
    for salesperson in sorted_salespeople:
        table.append([
            salesperson.name, #Name
            str(f"{salesperson.commission_rate:.2%}"), #Commission Rate
            str(f"${salesperson.total_sales():,.2f}"), #Sales
            str(f"${salesperson.calculate_pay():,.2f}"), #Commissions
            str(f"${(salesperson.base_salary/5) * (salesperson.days_worked):,.2f}"), #Base Pay
            str(f"${salesperson.bonus:,.2f}"), #Bonus Pay
            str(f"${salesperson.calculate_pay() + ((salesperson.base_salary/5) * (salesperson.days_worked)) + salesperson.bonus:,.2f}"), #Total Comp
            str(f"{salesperson.total_sales_count()}"), #Sales Count
            salesperson.attempts, #Sales Attempts
            str(f"{divZ(salesperson.total_sales_count(),salesperson.attempts):.1%}"), #Success Percentage
            str(f"${salesperson.total_sales() - (salesperson.calculate_pay() + ((salesperson.base_salary/5) * (salesperson.days_worked))):,.2f}"), #Company Profit Per Employee
            str(f"{salesperson.vacation_days_used}"), #Vacation Days
            str(f"{salesperson.days_worked - salesperson.vacation_days_used}") #Total Days Worked
                      ])
        
    table_2 = []
    table_2.append([
            len(salespeople), #Amount of employees
            "---", #Commission Rate
            str(f"${sum(salesperson.total_sales() for salesperson in sorted_salespeople):,.2f}"), #Sales
            str(f"${sum(salesperson.calculate_pay() for salesperson in sorted_salespeople):,.2f}"), #Commissions
            str(f"${sum((salesperson.base_salary/5) * (salesperson.days_worked) for salesperson in sorted_salespeople):,.2f}"), #Base Pay
            str(f"${sum(salesperson.bonus for salesperson in sorted_salespeople):,.2f}"), #Bonus Pay
            str(f"${sum(salesperson.calculate_pay() + ((salesperson.base_salary/5) * (salesperson.days_worked)) + salesperson.bonus for salesperson in sorted_salespeople):,.2f}"), #Total Comp
            str(f"{sum(salesperson.total_sales_count() for salesperson in sorted_salespeople)}"), #Sales Count
            sum(salesperson.attempts for salesperson in sorted_salespeople), #Sales Attempts
            str(f"{divZ(sum(salesperson.total_sales_count() for salesperson in sorted_salespeople),sum(salesperson.attempts for salesperson in sorted_salespeople)):.1%}"), #Success Percentage
            str(f"${sum(salesperson.total_sales() - (salesperson.calculate_pay() + ((salesperson.base_salary/5) * (salesperson.days_worked))) for salesperson in sorted_salespeople):,.2f}"), #Company Profit Per Employee
            str(f"{sum(salesperson.vacation_days_used for salesperson in sorted_salespeople)}"), #Vacation Days
            str(f"{sum(salesperson.days_worked - salesperson.vacation_days_used for salesperson in sorted_salespeople)}") #Total Days Worked
                      ])


    print("\nLeaderboard:\n")

    print(
        tabulate(
            table,
            headers,
            showindex=True,
            tablefmt="simple_grid",
            colalign=("left","right","right","right","right","right","right","right","right","right","right")
            ))
    
    print("\nCompany Totals:\n")

    print(
        tabulate(
            table_2,
            headers,
            showindex=True,
            tablefmt="simple_grid",
            colalign=("left","right","right","right","right","right","right","right","right","right","right")
            ))

    # print(f"{'Name':<10}{'Sales':>15}{'Commissions':>20}{'Base Pay':>20}{'Total Comp':>20}{'Sales Count':>15}{'Attempts':>10}{'Success %':>10}")
    
    # print("-----------------------------------------------------------------------")

    # sorted_salespeople = sorted(salespeople, key=lambda sp: sp.total_sales(), reverse=True)
    # for salesperson in sorted_salespeople:
    #     print(f"{salesperson.name:<10}{salesperson.total_sales():>14,.2f}{salesperson.calculate_pay():>19,.2f}{salesperson.base_salary * 52:>19,.2f}{salesperson.calculate_pay() + (salesperson.base_salary * 52):>19,.2f}{salesperson.total_sales_count():>14}{salesperson.attempts:>10}{salesperson.total_sales_count()/salesperson.attempts:>10,.2%}")


def setup_database():
    conn = sqlite3.connect('sales_results.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            employee TEXT,
            commission_rate REAL,
            sales REAL,
            commissions REAL,
            base_pay REAL,
            bonus REAL,
            total_comp REAL,
            sales_count INTEGER,
            attempts INTEGER,
            success_rate REAL,
            profit REAL,
            vacation_days_used INTEGER,
            days_worked INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_to_database(salespeople):
    conn = sqlite3.connect('sales_results.db')
    c = conn.cursor()

    for salesperson in salespeople:
        c.execute('''
            INSERT INTO results (employee, commission_rate, sales, commissions, base_pay, bonus, total_comp, sales_count, attempts, success_rate, profit, vacation_days_used, days_worked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            salesperson.name,
            salesperson.commission_rate,
            salesperson.total_sales(),
            salesperson.calculate_pay(),
            salesperson.base_salary / 5 * salesperson.days_worked,
            salesperson.bonus,
            salesperson.calculate_pay() + salesperson.base_salary / 5 * salesperson.days_worked + salesperson.bonus,
            salesperson.total_sales_count(),
            salesperson.attempts,
            divZ(salesperson.total_sales_count(), salesperson.attempts),
            salesperson.total_sales() - (salesperson.calculate_pay() + salesperson.base_salary / 5 * salesperson.days_worked),
            salesperson.vacation_days_used,
            salesperson.days_worked - salesperson.vacation_days_used
        ))

    conn.commit()
    conn.close()


def main():
    global days
    global salespeople
    global products

    with open('products.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product = Product(
                name=row['name'],
                price=float(row['price']),
                base_commission_rate=float(row['base_commission_rate']),
                add_commission_rate=float(row['add_commission_rate'])
            )
            products.append(product)

    if not salespeople:
        with open('roster.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                salesperson = Salesperson(
                    name=row['name'],
                    team=row['team'],
                    base_salary=float(row['base_salary']),
                    commission_rate=float(row['commission_rate']),
                    skill_level=float(row['skill_level']),
                    network_size=float(row['network_size']),
                    vacation_likelihood=float(row['vacation_likelihood']),
                    work_ethic=float(row['work_ethic']),
                )
                salespeople.append(salesperson)

    company = SalesCompany(salespeople, 0, 0, 0)
 
    for day in range(1, days + 1):
        for salesperson in salespeople:
            if not salesperson.take_vacation():
                company.generate_sales(salesperson)
            salesperson.days_worked += (days/5)
        company.update_payroll()
        company.update_profit()

        for salesperson in salespeople:
            salesperson.check_bonus()


    save_to_database(salespeople)  # Save the results to the database

    display_leaderboard(salespeople)
 



if __name__ == '__main__':
    setup_database()  # Set up the database the first time the script runs
    main()