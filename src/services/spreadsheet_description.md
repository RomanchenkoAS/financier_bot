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

E8 says "Any month" that is a table name
E9 says "year" and F9 is number of year (eg 2025)
E10 says "month" and F10 contains number of month (eg. 9)
E11 says "Total" and F11 contains sum of expenses for that month
formula:

```
=SUMIFS(data!C:C;data!A:A;">="&DATE(F9;F10;1);data!A:A;"<"&DATE(F9;F10+1;1))
```

Then column E13:E contains categories that are present in current month expenses

The formula is as follows:

```
=UNIQUE(
  FILTER(
    data!B:B;
    (data!A:A >= DATE(F9; F10; 1)) *
    (data!A:A < DATE(F9; F10 + 1; 1))
  )
)
```

And in column F13:F there are sums of expenses for each category
The formula:

```
=IF(E13="";"";SUMIFS(data!$C:$C;data!$B:$B;E13;data!$A:$A;">="&DATE($F$9;$F$10;1);data!$A:$A;"<"&DATE($F$9;$F$10+1;1)))
```

Next to it table "current month" which is very similar
G8 - title
H9 - current year
H10 - current month (eg. 9)
H11 - total for month
G13:G - categories in current month's expenses
H13:H - subtotals for categories
