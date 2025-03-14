import util
import time

DRIVER_LIST = util.session_driver_list(9686)
pos_list = util.get_last_drivers_position(9686, DRIVER_LIST)
print(util.pretty_output(pos_list))
