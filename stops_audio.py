import requests
from datetime import datetime
#import time, threading
import schedule
import os
import RPi.GPIO as GPIO

temp_list = []
new_info = {}

resources_path = "/home/pi/arrivals/audio_files/"

def get_API():

  info = {}
  stops = ["68", "70", "71", "78", "79", "770"]
  i = 0

  try:

    r = requests.get('https://api.metrocloudalliance.com/v2/realtime/predictions?api_key=demo&carrier_id=MT&stop_id=3103')#, params = "request_parameters")
    print("Getting API\n")

    api = r.json()

    for x in range(0, api["result_count"]):
      company = api["results"][x]

      for y in range(0, len(company["routes"])):
        info[i] = company["routes"][y]
        i+=1

    #print(info)

    for x in info:
      if info[x]["route"] in stops:
        try:

          if "schedule" in info[x]:
            time_list = info[x]["schedule"].get("times_minutes").split(",")
            new_time = int(time_list[0])

          if "VIA" in info[x]["pattern_name"]:

            name_list = info[x].get("pattern_name").split("VIA")
            new_name = name_list[0] + "\nVIA" + name_list[1]

            if "-" in new_name:
              name_list = new_name.split("-")
              new_name = name_list[0] + "\n" + name_list[1].strip()

          elif "-" in info[x]["pattern_name"]:

            name_list = info[x].get("pattern_name").split("-")
            new_name = name_list[0] + "\n" + name_list[1].strip()

            if "-" in new_name:
              name_list = new_name.split("-")
              new_name = name_list[0] + "\n" + name_list[1].strip()

          if "(" in new_name:
            temp = new_name.split("(")
            new_name = temp[0] + "\n(" + temp[1]

          route_list = info[x].get("route_name").split(" ")
          new_route = route_list[-1]

          if new_route[0].isnumeric() == False:
            new_route = info[x].get("route")

          new_info[x] = {"name" : new_name, "route" : new_route, "time" : new_time} 

        except:
          pass

    print(new_info)

    return True

  except:

    print("No connection to API\n")
    return False
    

def audio():

  current_Time = str(datetime.now().strftime("%H:%M %p"))
  print("Time: %s" % current_Time)

  if get_API():

    temp_list = sorted(new_info, key = lambda x:(new_info[x].get("time")))

    for n in range(0, 6):

      lines = str(new_info[temp_list[n]].get("route"))
      stops = str(new_info[temp_list[n]].get("name"))
      remaining_time = str(new_info[temp_list[n]].get("time"))

      if remaining_time == "5" or remaining_time == "1":#and speaker_flag == 0:
        GPIO.output(19, GPIO.HIGH)
        speaker_flag = speaker(lines, remaining_time)
        GPIO.output(19, GPIO.LOW)


def speaker(line, minutes):

  os.system("mpg321" + resources_path + line + "_" + minutes + "min.mp3")
  print("Bus " + line + " arrinving in " + minutes)

  return 1


def main():

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(19, GPIO.OUT)
  GPIO.output(19, GPIO.LOW)

  audio()

  schedule.every().minute.at(":00").do(audio)

  while True:

    schedule.run_pending()


if __name__=="__main__":

  main()
