#!/usr/bin/env python3

'''
A node to handle command from keyboard input
'''

from __future__ import print_function

import rospy
from std_msgs.msg import Float64
from open_base.msg import Movement

import sys, select, termios, tty

msg = """
Reading from the keyboard !
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .
For Holonomic mode (strafing), hold down the shift key:
---------------------------
   U    I    O
   J    K    L
   M    <    >
anything else : stop
q/z : increase/decrease max speeds by 10%
CTRL-C to quit
"""

# (vx, vy, w)
moveBindings = {
        'u': (1, 1, 1),
        'i': (1, 0, 0),
        'o': (1, -1, -1),
        'j': (0, 0, 1),
        'l': (0, 0, -1),
        'm': (-1, 1, 1),
        ',': (-1, 0, 0),
        '.': (-1, -1, -1),
        'U': (1, 1, 0),
        'I': (1, 0, 0),
        'O': (1, -1, 0),
        'J': (0, 1, 0),
        'L': (0, -1, 0),
        'M': (-1, 1, 0),
        '<': (-1, 0, 0),
        '>': (-1, -1, 0),
    }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
    }

def getKey():
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def vels(speed):
    return "currently:\tspeed %s " % (speed)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('vel_Publisher')
    pub_cmd = rospy.Publisher('/open_base/command', Movement, queue_size=1)


    speed = 1.0
    vx = 0
    vy = 0
    w = 0
    status = 0

    try:
        print(msg)
        print(vels(speed))
        while(1):
            key = getKey()
            if key in moveBindings.keys():
                vx = moveBindings[key][0]
                vy = moveBindings[key][1]
                w = moveBindings[key][2]
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]

                print(vels(speed))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:
                vx = 0
                vy = 0
                w = 0
                if (key == '\x03'):
                    break

            msg = Movement()
            
            msg.movement = 1

            msg.generic.type = 2
            msg.generic.frame = 1
            msg.generic.target.x = vx * speed
            msg.generic.target.y = vy * speed
            msg.generic.target.theta = w * speed

            pub_cmd.publish(msg)

    except Exception as e:
        print(e)

    finally:
        msg = Movement()

        msg.movement = 1

        msg.generic.type = 2
        msg.generic.frame = 1
        msg.generic.target.x = 0
        msg.generic.target.y = 0
        msg.generic.target.theta = 0

        pub_cmd.publish(msg)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)