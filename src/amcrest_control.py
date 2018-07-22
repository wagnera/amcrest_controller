import rospy, math
from amcrest import AmcrestCamera
from sensor_msgs.msg import Joy
from bisect import bisect_left #used for closest number calculation
class ros_amcrest:
	def __init__(self):
		self.cam = AmcrestCamera('192.168.1.108', 80, 'user', 'abc123abc').camera
		rospy.init_node('amcrest_controller', anonymous=True)
		rospy.Subscriber("/joy", Joy, self.joy_callback)
		self.init_move_logic()
		self.r = rospy.Rate(5)

	def init_move_logic(self):
		astep=45#math.radians(45) #angle step
		self.angles=[]
		self.speeds=range(9)
		for i in range(8):
			self.angles.append(i*astep)

	def joy_callback(self,data):
		self.last_joy=data

	def move(self):
		try:
			joy_data=self.last_joy
		except:
			return
		x=-joy_data.axes[3] #collect joy stick position
		y=-joy_data.axes[4]
		angle=math.atan2(y,x) #calcualte angle
		mag=math.sqrt(x**2+y**2)
		if angle < 0: #check if in 3 and 4 quadrant and convert to angle from +x
			angle = angle + 2*math.pi
		angle=math.degrees(angle) #convert to degrees
		joy_angle=takeClosest(self.angles, angle)#get closest multiple of 45 to measured angle
		joy_mag=takeClosest(self.speeds,mag*8)
		if joy_mag > 0:
			#print(joy_angle,joy_mag) #Debug

			#Call correct command based on angle:
			if joy_angle == 0:
				self.cam.move_right(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 45:
				self.cam.move_right_up(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 90:
				self.cam.move_up(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 135:
				self.cam.move_left_up(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 180:
				self.cam.move_left(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 225:
				self.cam.move_left_down(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 270:
				self.cam.move_down(action="start", channel=0, vertical_speed=joy_mag)
			elif joy_angle == 315:
				self.cam.move_right_down(action="start", channel=0, vertical_speed=joy_mag)
		else:
			self.cam.move_right(action="stop", channel=0, vertical_speed=0) #stop motor if no speed requested


	def spinner(self):
		while not rospy.is_shutdown():
			self.move()
			self.r.sleep()

def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

a=ros_amcrest()
a.spinner()
