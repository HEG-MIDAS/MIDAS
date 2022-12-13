from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import datetime
import numpy

database = "midas"
retention_policy = 'autogen'

def queryTest(device = None):
    with connectToDB() as client:
        bucket = f'{database}/{retention_policy}'
        data = {}
        # Initiate Query API
        query_api = client.query_api()
        # Create Query
        ## Filter by Device if one is provided
        devicetoadd = f'|> filter(fn: (r) => r["end device"] == "{device}")' if device != None else ""
        ## range specify timestamp, can include a start and stop
        ## lowestAverage takes all lines in DB with same timestamp,
        ### measurements and device and average them so it returns only 1
        ## keep only show specified columns
        ## pivot allows us to have 1 line with all measurements
        ## sort sort the response by provided columns
        query = f'''from(bucket: "{bucket}")
        |> range(start: -1y)
        |> lowestAverage(n: 1000, groupColumns: ["_start","_field","end device"])
        |> keep(columns: ["_start","_field","_value","end device"])
        |> pivot(rowKey: ["_start","end device"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["end device","_start"])
        {devicetoadd}'''
        tables = query_api.query_csv(query)
        for row in tables:
            print(row[3:])

        return data

def query(device = None):
    with connectToDB() as client:
        bucket = f'{database}/{retention_policy}'
        data = {}
        # Initiate Query API
        query_api = client.query_api()
        # Create Query
        ## range determine start of query
        devicetoadd = f'|> filter(fn: (r) => r["end device"] == "{device}")' if device != None else ""
        query = f'''from(bucket: "{bucket}")
        |> range(start: -1y)
        |> sort(columns: ["end device","_start"])
        {devicetoadd}'''
        # Query Data in CSV Format
        tables = query_api.query_csv(query)
        for row in tables:
            if len(row) > 0 and not row[0].startswith('#'):
                # This is always empty, delete it to be safe
                del row[0]
                # cast row part to variable
                station = row[-1]
                # Try to cast timestamp into datetime or let it empty (header)
                try:
                    timestamp = datetime.datetime.strptime(row[2].split(".")[0],"%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                except:
                    timestamp = row[2]
                measurement = row[-3]
                value = row[-4]
                # Add station to array if not found
                if(station not in data):
                    data[station] = {}
                if(timestamp not in data[station]):
                    data[station][timestamp] = {}
                # Add measurement to array if not found
                if(measurement not in data[station][timestamp]):
                    data[station][timestamp][measurement] = []
                # Try to add value as a float
                try:
                    data[station][timestamp][measurement].append(float(value))
                # If fail (header), add it as a string
                except:
                    if(value not in data[station][timestamp][measurement]):
                        data[station][timestamp][measurement].append(value)
        # New loop in dict to average values
        for station in data:
            for timestamp in data[station]:
                for measurement in data[station][timestamp]:
                    value_arr = data[station][timestamp][measurement]
                    if(type(value_arr[0])==float):
                        data[station][timestamp][measurement] = numpy.average(value_arr)
        return data

def connectToDB():
    # Create Bucket to be used by lib
    return InfluxDBClient.from_config_file(f'{os.path.join(os.getcwd(), os.path.dirname(__file__))}/config.ini')

def main():
    data = queryTest()
    print(data)
    # Missing write to file

if __name__ == "__main__":
    main()
