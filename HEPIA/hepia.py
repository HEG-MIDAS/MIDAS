from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
database = "midas"
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'
with InfluxDBClient.from_config_file(f'{os.path.join(os.getcwd(), os.path.dirname(__file__))}/config.ini') as client:
    print('*** Query Points ***')

    query_api = client.query_api()
    query = f'from(bucket: \"{bucket}\") |> range(start: -1h)'
    tables = query_api.query(query)
    for record in tables[0].records:
        print(f'#{record.get_time()} #{record.get_measurement()}: #{record.get_field()} #{record.get_value()}')
