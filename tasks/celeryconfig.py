# import tasks
imports = (
    'tasks.ask',
    'tasks.webcast'
    )

# #Timezone
enable_utc=False
timezone='Asia/Taipei'

# Broker and Backend
broker_url = 'redis://172.30.226.220:63792/0'
result_backend = 'redis://172.30.226.220:63792/0'


