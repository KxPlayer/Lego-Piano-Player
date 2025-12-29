from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

# Standard MicroPython modules
from usys import stdin, stdout
from uselect import poll

motor1 = Motor(Port.A)
motor2 = Motor(Port.B)

while True:

    # Let the remote program know we are ready for a command.
    stdout.buffer.write(b"rdy")

    # Read integer from outside file.
    cmd = stdin.buffer.read(1)
    val = int.from_bytes(cmd, 'big', False)

    # Why is from_bytes still bugged???
    if val > 127:
        val = val - 256

    # 48 - C3
    if val == 48:
        motor1.track_target(90)
    elif val == -48:
        motor1.track_target(0)
    # 50 - D3
    elif val == 50:
        motor2.track_target(90)
    elif val == -50:
        motor2.track_target(0)
    # 0 - stops motor from reading values
    elif val == 0:
        # Stops everything
        break
    # Ignores all other values if nothing found
