# AutoFinanceBot

<b>DATABASE DESIGN </b><br>
- Expenses table
- Income table
- Recurring table

<h5>Expenses Table</h5>
- ID:string
- Category:string
- Description:string (VARCHAR30)
- Date:timestamp
- Amount:float

<h5>Income Table</h5>
- ID:string
- Category:string
- Description:string (VARCHAR30)
- Date:timestamp
- Amount:float

<h5>Recurring Table</h5>
- ID:string
- Type:string
- Category:string
- Description:string
- Schedule:int(0:daily | 1-7:weekly | 8.9.10: monthly)
- Enabled:bool(default:True)
- Amount:float

<h4>DB API</h4>
- Insert
    - Expense
    - Income
    - Recurring
- Delete
    - Expense
    - Income
    - Recurring
- Update
    - Disable recurring
    - Update recurring
    

<h4>Bugs</h4>

- Major
    - Have to handle dictionary key errors upon restart
    - Enable feature to check if records >= 3, stop inserting
    - Should show user how many daily free entries left
- Minor
    - Recurring entries not complete
    - There should be indicator to know if expense/incomes are recurring or not (True/False boolean)