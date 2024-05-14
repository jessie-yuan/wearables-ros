#!/usr/bin/env python

import rospy
from std_msgs.msg import Char
import sys, select
import tty, termios

def getKey():
    old_settings = termios.tcgetattr(sys.stdin.fileno())

    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return key

def keyboard():
    pub = rospy.Publisher('control_obi', Char, queue_size=1)
    rospy.init_node('keyboard')
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        key = getKey()
        if key == 'w':
            msg = 1
        elif key == 's':
            msg = 2
        else:
            msg = 0
        rospy.loginfo(msg)
        pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        keyboard()
    except rospy.ROSInterruptException:
        pass

#python3 ~/wearables_ws/src/wearables_ros/scripts/keyboard.py