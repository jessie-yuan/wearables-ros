#!/usr/bin/env python
import time, rospy
from obimovement import ObiMovement
from std_msgs.msg import Char

direction = 0

def callback(data):
    global direction
    direction = data.data
    #rospy.loginfo("from callback fn: %d", direction)

if __name__ == '__main__':

    obirobot = ObiMovement(0)
    try:
        rospy.init_node('obi')
        rospy.Subscriber("control_obi", Char, callback)

        rate = rospy.Rate(10) # 10hz
        while not rospy.is_shutdown():
            #rospy.loginfo("from main: %d", direction)
            if direction == 1:
                obirobot.advance_stage()
            if direction == 2:
                obirobot.decrease_stage()
            rate.sleep()

        obirobot.close()

    except rospy.ROSInterruptException:
        obirobot.close()

