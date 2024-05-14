import obi, time, csv
import numpy as np

with open('saved-positions/bowls.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  BOWL_COORDS = list(csv_reader)

with open('saved-positions/bowl0-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_0 = list(csv_reader)[:-1]

with open('saved-positions/bowl1-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_1 = list(csv_reader)[:-1]

with open('saved-positions/bowl2-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_2 = list(csv_reader)[:-1]

with open('saved-positions/bowl3-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_3 = list(csv_reader)[:-1]

with open('saved-positions/bowls.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  HOME = list(csv_reader)[0]

with open('saved-positions/mouth-pos.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  MOUTH_POS = list(csv_reader)[0]

NUM_STEPS = 8

def interpolate():
  res = []
  start_vector = np.array(HOME).astype(int)
  end_vector = np.array(MOUTH_POS).astype(int)
  for i in range(NUM_STEPS):
    fraction = i / (NUM_STEPS - 1)
    vector = start_vector + (end_vector - start_vector) * fraction
    res.append(vector.astype(int).tolist())
  return res

MOUTH_TRAJ = interpolate()

class ObiMovement():
  def __init__(self, my_bowlno):
    self.robot = obi.Obi('/dev/ttyUSB0') # run sudo chmod a+rw /dev/ttyUSB0
    self.speed = 6000
    self.accel = 16000
    self.mouthpos = MOUTH_POS
    self.stage = 0 # 0 = just started; 1 = just scooped; 2-NUM_STEPS = along traj to mouth; NUM_STEPS+1 = at mouth
    self.bowlno = my_bowlno
    print(self.robot.SerialIsOpen())
    print(self.robot.VersionInfo())
    self.robot.Wakeup()
    self.robot.WaitForCMUResponse()
    print("I'm up!")

  def scoop_from_bowlno(self):
    print(f"Scooping from bowl {str(self.bowlno)} at max speed {self.speed} and max accel {self.accel}")
    if self.bowlno == 0:
      waypoints = SCOOP_0
    elif self.bowlno == 1:
      waypoints = SCOOP_1
    elif self.bowlno == 2:
      waypoints = SCOOP_2
    else:
      waypoints = SCOOP_3
    
    for i in range(9):
      waypoint = waypoints[i] + [self.speed, self.accel, 0]
      self.robot.SendOnTheFlyWaypointToObi(i, waypoint)
    self.robot.ExecuteOnTheFlyPath()
    self.robot.WaitForCMUResponse()

  def move_to_mouth(self):
    self.just_scraped = False
    print(f"Moving to mouth at max speed {self.speed} and max accel {self.accel}")
    waypoint = self.mouthpos + [self.speed, self.accel, 0]
    self.robot.SendOnTheFlyWaypointToObi(0, waypoint)
    self.robot.ExecuteOnTheFlyPath()
    self.robot.WaitForCMUResponse()

  def advance_stage(self):
    if self.stage == 0 or self.stage == NUM_STEPS + 1:
      self.scoop_from_bowlno()
      self.stage = 1
    else:
      waypoint = MOUTH_TRAJ[self.stage - 1] + [self.speed, self.accel, 0]
      self.robot.SendOnTheFlyWaypointToObi(0, waypoint)
      self.robot.ExecuteOnTheFlyPath()
      self.robot.WaitForCMUResponse()
      self.stage += 1
      if self.stage == NUM_STEPS + 1:
        time.sleep(2)

  def decrease_stage(self):
    if self.stage in range(3, NUM_STEPS + 2):
      waypoint = MOUTH_TRAJ[self.stage - 3] + [self.speed, self.accel, 0]
      self.robot.SendOnTheFlyWaypointToObi(0, waypoint)
      self.robot.ExecuteOnTheFlyPath()
      self.robot.WaitForCMUResponse()
      self.stage -= 1

  def close(self):
    self.robot.GoToSleep()
    self.robot.Close()
    print(self.robot.SerialIsOpen())
    print("All done")