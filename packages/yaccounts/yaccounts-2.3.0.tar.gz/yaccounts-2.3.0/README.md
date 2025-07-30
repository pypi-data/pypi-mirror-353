# yaccounts Package
#### Scripts for generating BYU accounting reports with the new Workday system

## Installation
It is recommended that you first create a Python virtual environment to avoid conflicts with other packages. 

    python3 -m venv venv

Activate the virtual environment in your terminal (this needs to be done each time you open a new terminal session):
- On Windows:
    ```
    venv\Scripts\activate
    ```
- On macOS/Linux:
    ```
    source venv/bin/activate
    ```

Then install the package using pip:

    pip install yaccounts


## Command-Line Usage

1. **First run Chrome.**  This will run chrome with a remote debugging port open, and uses a new user profile so that it does not interfere with your normal Chrome profile.  When this window opens, you will need to log in to Workday with your BYU credentials, then return to the terminal and hit enter to continue.
    
        yaccounts run-chrome

2. **Actuals Report**. Then you can run the following to collect month-by-month actuals for a given account. 

        yaccounts report-actuals GR01410

3. **Payroll Data**. You can add payroll data to your report by first running the the following command to collect payroll data for all of your grants for the year, which will generate a file called *payroll_2025.pkl*.

        yaccounts get-payroll

    Provide this payroll data to the actuals report by running:

        yaccounts report-actuals GR01410 --payroll-pkl payroll_2025.pkl

4. **Journal Data**.  You can collected detailed journal entries that will provide a line-by-line breakdown of the actuals report by adding `--add-journals` to the command.  This will make the report take about twice as long to run, but will provide a lot more detail. You can combine this with the payroll data as well:

        yaccounts report-actuals GR01410 --payroll-pkl payroll_2025.pkl --add-journals

    *Note:* The produced Excel file will have hidden rows with the journal entries. Click the '+' buttons on the left side of the sheet to expand these rows and see the journal entries.

## Python Usage

You can also use the package in Python code.  First, install the package as described above, then you can use it like this:

```python

from yaccounts import Account, PayrollData, run_chrome, get_chrome_webdriver


def main():
    run_chrome()

    dr = get_chrome_webdriver()

    payroll = PayrollData(2025)
    payroll.get_workday_data(dr)

    account = Account("GR00227", 2025)
    account.get_workday_data(dr)
    account.add_payroll_data(payroll)
    account.to_excel()
```

## FAQ

#### **Q: Can I run multiple reports at once?**

**A:** No, I hope to add this in the future, but for now you can only run one account at a time.



#### **Q: Can I export the payroll data to Excel?**

**A:** Yes, you can export the payroll data to Excel by adding the `--xlsx-out-path <file>` argument to the `get-payroll` command. 

#### **Q: Can I export the journal entries to Excel?**
**A:** Yes, you can export the journal entries to Excel by adding the `--journals-xlsx-out <file>` argument to the `report-actuals` command.

## Makefile

Here is a Makefile I use to run all my accounts:

```makefile
IN_ENV := . .venv/bin/activate;

YEAR := 2025

ACCOUNTS := \
    sandia:GR01410 \
    onr:GR01172 \
    consolidated:AC07190 \
    gift:GF02905

ACCOUNT_NAMES := $(foreach pair, $(ACCOUNTS), $(firstword $(subst :, ,$(pair))))

all_accounts: $(foreach name, $(ACCOUNT_NAMES), $(name)_${YEAR}.xlsx)

env: .venv/bin/activate

.venv/bin/activate: requirements.txt
	python3 -m venv .venv
	$(IN_ENV) pip install yaccounts

chrome:
	$(IN_ENV) yaccounts run-chrome

payroll: payroll_${YEAR}.pkl

payroll_${YEAR}.pkl:
	$(IN_ENV) yaccounts get-payroll --year ${YEAR} --pkl-out $@

clean:
	rm -f $(foreach acc, $(ACCOUNTS), $(acc)_${YEAR}.xlsx) payroll_${YEAR}.pkl

# Pattern rule for each account
%_${YEAR}.xlsx: payroll_${YEAR}.pkl
	$(IN_ENV) yaccounts report-actuals $(call get_code,$*) --payroll-pkl $< --xlsx-out $@ --year ${YEAR} --add-journals

# Function to extract the code given a name
get_code = $(word 2, $(subst :, ,$(filter $1:%,$(ACCOUNTS))))
```