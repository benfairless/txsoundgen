# # import sys
# import yaml
import boto3

client = boto3.client("polly")


# with open('packs/en.yaml') as f:
#     data = yaml.load(f, Loader=yaml.FullLoader)
# b = Pack(client, data)
# b.process()
# print(b.path)
# b.generate()

# from txsoundgen import environment
# from txsoundgen.model import CachedSound, db, Sound
# if environment == 'development':
#     db.init(':memory:', pragmas = { 'journal_mode': 'wal' })
# # else:
# #     db.init('cache.db', pragmas = { 'journal_mode': 'wal' })
# db.create_tables([CachedSound])


# from txsoundgen.model import Sound
# # from txsoundgen import db
# # db.init(':memory:', pragmas = { 'journal_mode': 'wal' })
# # db = peewee.SqliteDatabase('cache.sqlite', pragmas = { 'journal_mode': 'wal' })
# # db.create_tables([CachedSound])
# # if db.connect():
# #     print('true')


data = {"sounds": {"system": {"1": "Hello"}, "extra": {"weirdlong": "Goodbye"}}}

from txsoundgen.pack import Pack

pack = Pack(data)
print(pack.list)
