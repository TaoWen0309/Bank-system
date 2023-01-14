from flask_table import Table, Col
 
class record_results(Table):
    number = Col('AccountNumber')
    card = Col('Card')
    time = Col('Time')
    abstract = Col('Abstract')
    other_number = Col('OtherNumber')
    amount = Col('Amount')
    balance_before = Col('BalanceBefore')
    balance_after = Col('BalanceAfter')