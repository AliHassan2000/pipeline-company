from __future__ import unicode_literals, print_function
import time
from netmiko import ConnectHandler, redispatch

print("Connecting")
net_connect = ConnectHandler(
    device_type='terminal_server',        # Notice 'terminal_server' here
    ip='10.14.93.27', 
    username='srv00280', 
    password='1a3X#eEW3$40vPN%'
    )

# Manually handle interaction in the Terminal Server 
# (fictional example, but hopefully you see the pattern)
# Send Enter a Couple of Times
import pdb;pdb.set_trace()
net_connect.write_channel("\r\n")
time.sleep(1)
net_connect.write_channel("\r\n")
time.sleep(1)
output = net_connect.read_channel()
print(output)                             # Should hopefully see the terminal server prompt

# Login to end device from terminal server
net_connect.write_channel("connect 1\r\n")
time.sleep(1)

# Manually handle the Username and Password
max_loops = 10
i = 1
while i <= max_loops:
    output = net_connect.read_channel()
    
    if 'Username' in output:
        net_connect.write_channel(net_connect.username + '\r\n')
        time.sleep(1)
        output = net_connect.read_channel()

    # Search for password pattern / send password
    if 'Password' in output:
        net_connect.write_channel(net_connect.password + '\r\n')
        time.sleep(.5)
        output = net_connect.read_channel()
        # Did we successfully login
        if '>' in output or '#' in output:
            break

    net_connect.write_channel('\r\n')
    time.sleep(.5)
    i += 1

# We are now logged into the end device 
# Dynamically reset the class back to the proper Netmiko class
redispatch(net_connect, device_type='cisco_ios')

# Now just do your normal Netmiko operations
new_output = net_connect.send_command("show ip int brief")