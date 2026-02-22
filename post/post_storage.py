class PostParkingAvailabilityRepository:
    def __init__(self, table_resource):
        self.table = table_resource

    def store(self, item):
        self.table.put_item(Item=item)
