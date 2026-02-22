from boto3.dynamodb.conditions import Key


class GetParkingAvailabilityHandler:
    def __init__(self, table_resource):
        self.table = table_resource

    def handle(self, path_params):
        lot_num = (path_params or {}).get('lotNum')

        if not lot_num:
            return 400, {"message": "lotNum is required"}

        try:
            lot_num = int(lot_num)
        except ValueError:
            return 400, {"message": "lotNum must be a number"}

        query_kwargs = {
            'KeyConditionExpression': Key('lotNum').eq(lot_num),
            'Limit': 1,
            'ScanIndexForward': False,
        }

        query_response = self.table.query(**query_kwargs)
        items = query_response.get('Items', [])

        if not items:
            return 200, {
                "message": f"No parking data found for lot {lot_num}",
                "data": None,
            }

        return 200, {
            "message": f"Most recent parking availability for lot {lot_num}",
            "data": items[0],
        }
