# rtcdp/cli/query_cli.py

from rtcdp.api.modules.inspect_data.queries import QueryHandler

def query_menu():
    handler = QueryHandler()
    handler.handle_queries()
