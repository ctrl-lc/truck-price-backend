class Batch:
    def __init__(self, db):
        self.db = db


    def __enter__(self):
        self.new_batch()
        return self


    def __exit__(self, a1, a2, a3):
        if self.operations_queued > 0:
            self.batch.commit()


    def register_new_operation(self):
        self.operations_queued += 1
        if self.operations_queued >= 500:
            self.batch.commit()
            self.new_batch()


    def new_batch(self):
        self.batch = self.db.batch()
        self.operations_queued = 0


    def set(self, *args, **kwargs):
        self.batch.set(*args, **kwargs)
        self.register_new_operation()


    def delete(self, *args, **kwargs):
        self.batch.delete(*args, **kwargs)
        self.register_new_operation()


    def update(self, *args, **kwargs):
        self.batch.update(*args, **kwargs)
        self.register_new_operation()