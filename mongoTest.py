import timeit

print 'w/out cache:',
print timeit.Timer(
"var2 = db.user.find_one({'_id': 'admin'})",
"""
import pymongo
c = pymongo.Connection()
db = c.csd
variable = db.user.find_one({'_id': 'admin'})
"""
).timeit(9999)

print 'w/ cache:',
print timeit.Timer(
"var2 = variable",
"""
import pymongo
c = pymongo.Connection()
db = c.csd
variable = db.user.find_one({'_id': 'admin'})
"""
).timeit(9999)

#trial 1:
#w/out cache: 2.28104400635
#w/ cache: 0.000303983688354

#trial 2:
#w/out cache: 2.29622411728
#w/ cache: 0.00031304359436

#trial 3:
#w/out cache: 2.10840296745
#w/ cache: 0.000303983688354

#trial 4:
#w/out cache: 2.11012601852
#w/ cache: 0.000333070755005

#trial 5:
#w/out cache: 2.25762796402
#w/ cache: 0.000303983688354


import pymongo
c = pymongo.Connection()
db = c.csd

variable = db.user.find_one({'_id': 'admin'})  # query is stored in variable
variable['account']['password'] = 'superpass'  # variable and mongo are updated



