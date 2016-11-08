from extract_daily_step import extract_daily_step as ed
import json

filename = "test.json"
f = open(filename, 'r')
js = json.loads(f.read())
f.close()

ed("/asd/234json", filename)
