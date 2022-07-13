# from txsoundgen import logger


# def worker(generator, sound):
#     try:
#         sound.generate(generator)
#     except Exception as e:
#         logger.error(e)
#         # logger.critical(f'{sound} has no ')
#         # raise Exception('ooo')


# def queue(generator, worklist: list, workers=3):
#     from concurrent.futures import ThreadPoolExecutor

#     with ThreadPoolExecutor(max_workers=workers) as executor:
#         for item in worklist:
#             executor.submit(worker, generator, item)


# # from concurrent.futures import ThreadPoolExecutor

# # ff = ['one', 'two', 'three', 'fish']

# # with ThreadPoolExecutor(max_workers=3) as executor:
# #     for i in ff:
# #         executor.submit(worker, f, Sound(i))
