
import curses
from Adafruit_PWM_Servo_Driver import PWM

# Initialise the PWM device using the default address
pwm = PWM(0x40, debug=False)

servoMin = 150  # Min pulse length out of 4096
servoMax = 610  # Max pulse length out of 4096



base_minDegree = 56
base_maxDegree = 200 # Degrees your servo can rotate
base_home = 82

shoulder1_minDegree = 120
shoulder1_maxDegree = 530
shoulder1_home = 182

shoulder2_maxDegree = 120
shoulder2_minDegree = 0
shoulder2_home = 160

elbow_maxDegree = 204
elbow_minDegree = 130
elbow_home = 166

degIncrease = 2  # Number of degrees to increase by each time
p = 0
pwm.setPWMFreq(60) # Set PWM frequency to 50Hz, HITEC recommended

def setDegree(channel, d, maxDeg):
    degreePulse = servoMin
    degreePulse += int((servoMax - servoMin) / 180) * d
    pwm.setPWM(channel, 0, degreePulse)

# Set up curses for arrow input
scr = curses.initscr()
curses.cbreak()
scr.keypad(1)
scr.addstr(0, 0, "Servo Manual Control")
scr.addstr(1, 0, "LEFT for base rotation left")
scr.addstr(2, 0, "RIGHT for base rotation right")
scr.addstr(3, 0, "UP for shoulder move up")
scr.addstr(4, 0, "DOWN for shoulder move down")
scr.addstr(5, 0, "PAGE_UP for elbow extend out")
scr.addstr(6, 0, "PAGE_DOWN for elbow extend in")
scr.addstr(7, 0, "HOME for shoulder rotate left")
scr.addstr(8, 0, "END for shoulder rotate right")
scr.addstr(9, 0, "q to quit")
scr.refresh()

#Set store Position
base_degree = base_home
shoulder1_degree = shoulder1_home
shoulder2_degree = shoulder2_home
elbow_degree = elbow_home

setDegree(0, base_degree, base_maxDegree)
setDegree(1, shoulder1_degree, shoulder1_maxDegree)
setDegree(2, elbow_degree, elbow_maxDegree)
setDegree(3, shoulder2_degree, shoulder2_maxDegree)


#ch0 - Base - LEFT/RIGHT
#ch1 - shoulder up/down - UP/DOWN
#ch2 - elbow - PAGEUP/PAGEDOWN
#ch3 - shoulder rotate - HOME/END


key = ''
while key != ord('q'):
    key = scr.getch()


    if key == curses.KEY_LEFT:
      base_degree += degIncrease

      #if base_degree > base_maxDegree:
      #   base_degree = base_maxDegree
      p = int((servoMax - servoMin) / 180) * base_degree
      setDegree(0, base_degree, base_maxDegree)

    elif key == curses.KEY_RIGHT:
       base_degree -= degIncrease

       #if base_degree < base_minDegree:
       #   base_degree = base_minDegree
       p = int((servoMax - servoMin) / 180) * base_degree
       setDegree(0, base_degree, base_maxDegree)

    elif key == curses.KEY_UP:
       shoulder1_degree -= degIncrease

       #if shoulder1_degree < shoulder1_minDegree:
       #  shoulder1_degree = shoulder1_minDegree
       p = int((servoMax - servoMin) / 180) * shoulder1_degree
       setDegree(1, shoulder1_degree, shoulder1_maxDegree)

    elif key == curses.KEY_DOWN:
       shoulder1_degree += degIncrease

       #if shoulder1_degree > shoulder1_maxDegree:
       #  shoulder1_degree = shoulder1_maxDegree
       p = int((servoMax - servoMin) / 180) * shoulder1_degree
       setDegree(1, shoulder1_degree, shoulder1_maxDegree)

    elif key == curses.KEY_HOME:
       shoulder2_degree -= degIncrease

       #if shoulder2_degree < shoulder2_minDegree:
       #  shoulder2_degree = shoulder2_minDegree
       p = int((servoMax - servoMin) / 180) * shoulder2_degree
       setDegree(3, shoulder2_degree, shoulder2_maxDegree)

    elif key == curses.KEY_END:
       shoulder2_degree += degIncrease

       #if shoulder2_degree > shoulder2_maxDegree:
       #  shoulder2_degree = shoulder2_maxDegree
       p = int((servoMax - servoMin) / 180) * shoulder2_degree
       setDegree(3, shoulder2_degree, shoulder2_maxDegree)

    elif key == curses.KEY_NPAGE:
       elbow_degree -= degIncrease

       #if elbow_degree < elbow_minDegree:
       #  elbow_degree = elbow_minDegree
       p = int((servoMax - servoMin) / 180) * elbow_degree
       setDegree(2, elbow_degree, elbow_maxDegree)

    elif key == curses.KEY_PPAGE:
      elbow_degree += degIncrease

      #if elbow_degree > elbow_maxDegree:
      #  elbow_degree = elbow_maxDegree
      p = int((servoMax - servoMin) / 180) * elbow_degree
      setDegree(2, elbow_degree, elbow_maxDegree)

    elif key == curses.KEY_IC:
      s = "                                        "
      scr.addstr(10, 0, s)
      scr.addstr(11, 0, s)
      scr.refresh()
      scr.addstr(11, 0 , str(p))
      s = 'B:' + str(base_degree) + ' S1:' + str(shoulder1_degree) + ' S2:' + str(shoulder2_degree) + ' E:' + str(elbow_degree)
      scr.addstr(10, 0, s)
      scr.refresh()


curses.endwin()
