from redis import Redis
from redis.commands.search.query import Query

def get_user_transactions(r: Redis, user_id: str):
    query_string = f"@user_id:{{{user_id}}}"
    result = r.ft("transactions-index").search(Query(query_string))
    return result.docs
