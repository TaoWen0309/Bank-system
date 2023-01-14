from flask_table import Table, Col, LinkCol
 
class user_results(Table):
    id = Col('Id')
    name = Col('Name')
    sex = Col('Sex')
    birth = Col('Birthday')
    phone_number = Col('PhoneNumber')
    edit = LinkCol('Edit', 'edit_view', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_user', url_kwargs=dict(id='id'))
    query = LinkCol('Query','query', url_kwargs=dict(id='id'))