import flet as ft, database_simple

db_obj=database_simple.Database(True, database='AdminInfo', user='postgres', password='5525', port='5890', host='localhost')

def test_page(page:ft.Page):
    table_obj=db_obj.get_table_obj('equipment')
    table=table_obj.getTable(db_obj)
    page.add(table)

ft.app(test_page)