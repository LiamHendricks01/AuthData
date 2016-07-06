USERS = {'editor': 'editor','Admin':'Admin',
         'viewer': 'viewer'}
GROUPS = {'editor': ['group:editors'],'Admin': ['group:editors']}


def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
