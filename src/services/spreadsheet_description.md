# Spreadsheet description

Spreadsheet page with data = "data"
Spreadsheet page with service info = "service"

Data page contains a table at columns A through D, header row is 6, first row with data is 7
This value "first row with data" is saved at page service at B2

## Columns

Column A: Date formatted as "23.09.2025"
Column B: Category
Column C: Expense sum
Column D: Note/comment

## Adding a row

New row should be inserted at the top of the table, above "first row with data"

## Service page

### Expenses distribution for a given month

E1 says "Any month" that is a table name
F1 says "month" and G1 contains number of month (eg. 9)
F2 says "Total" and G2 contains sum of expenses for that month
Then column F4:F contains categories that are present in current month expenses
And in column G4:G there are sums of expenses for each category

Next to it table "current month" which is very similar
H1 - title
J1 - current month (eg. 9)
J2 - total for month
I4:I - categories in current month's expenses
J4:J - subtotals for categories
