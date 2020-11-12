from datasette import hookimpl
from datasette.utils.asgi import Response
from .utils import get_searchable_tables, has_searchable_tables
import json


@hookimpl
def menu_links(datasette):
    async def inner():
        if await has_searchable_tables(datasette):
            return [
                {"href": datasette.urls.path("/-/search"), "label": "Search all tables"}
            ]

    return inner


async def search_all(datasette, request):
    searchable_tables = list(await get_searchable_tables(datasette))
    tables = [
        {
            "database": database,
            "table": table,
            "url": datasette.urls.table(database, table),
            "url_json": datasette.urls.table(database, table, format="json"),
        }
        for database, table in searchable_tables
    ]
    return Response.html(
        await datasette.render_template(
            "search_all.html",
            {
                "q": request.args.get("q") or "",
                "searchable_tables": tables,
                "searchable_tables_json": json.dumps(tables, indent=4),
            },
        )
    )


@hookimpl
def extra_template_vars(template, datasette):
    if template != "index.html":
        return
    # Add list of searchable tables
    async def inner():
        searchable_tables = list(await get_searchable_tables(datasette))
        return {"searchable_tables": searchable_tables}

    return inner


@hookimpl
def register_routes():
    return [
        ("/-/search", search_all),
    ]
