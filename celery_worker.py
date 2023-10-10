from app import create_app,celery

app = create_app('default')
print("celery  worker  create  app  complete!")
app.app_context().push()
print("celery  worker   complete!")
