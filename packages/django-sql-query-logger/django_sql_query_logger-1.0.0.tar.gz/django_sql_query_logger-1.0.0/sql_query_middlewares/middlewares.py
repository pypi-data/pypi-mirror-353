import logging

from django.db import connection


class QueryLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        response = self.get_response(request)

        total_time = 0
        total_joins = 0

        for query in connection.queries:
            query_time = query.get("time")
            if query_time is None:
                query_time = query.get("duration", 0) / 1000
            total_time += float(query_time)

            query_str = query.get("sql", "").upper()
            join_count = (
                query_str.count(" JOIN ")
                + query_str.count(" INNER JOIN ")
                + query_str.count(" LEFT JOIN ")
                + query_str.count(" RIGHT JOIN ")
            )
            total_joins += join_count

        query_count_str = "%s QUERIES | %s JOINS | %s SECONDS" % (
            len(connection.queries),
            total_joins,
            total_time,
        )

        print(f"\n{'#' * 30}\t{query_count_str}\t{'#' * 30}")

        return response
