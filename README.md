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
- Amount:float
