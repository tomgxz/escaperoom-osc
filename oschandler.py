from pythonosc import udp_client, dispatcher, osc_server
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

'''
pos5	 6.0345025	 2.9630268      x range -9.6 to 10.4    diff 20     per square 1.6r     half 0.83r      half 0.45
pos5	 6.0344      2.9630866      z range -4.1 to 5.7     diff 9.8    per square 0.816r   half 0.4083r    half 0.21

pos4	 0.69855934	 1.5890018      x range -10 to 11       diff 21     per square 1.75     half 0.875      half 0.45
pos4	 0.69857436	 1.5889034      z range -3.3 to 6.5     diff 9.8    per square 0.816r   half 0.4083r    half 0.21

pos3	-4.5688963	 2.3525424      x range -10.6 to 11     diff 21.6   per square 1.8      half 0.9        half 0.45
pos3	-4.568933	 2.3526065      z range -3.85 to 5.6    diff 9.45   per square 0.7875   half 0.39375    half 0.21

pos2	 8.82264    -2.9917376      x range -9.7 to 10.9    diff 20.6   per square 1.716r   half 0.8583r    half 0.45
pos2	 8.822644	-2.9916458      z range -4.4 to 5.4     diff 9.8    per square 0.816r   half 0.4083r    half 0.21
'''



# first position must be smaller than second position
CONFIG:dict = {
    "positions": [
        {
            "x1": 5.58,
            "x2": 6.48,
            "z1": 3.17,
            "z2": 3.75,
            "valid": False,
            "pointer": None,
        },
        {
            "x1": 0.25,
            "x2": 1.15,
            "z1": 1.39,
            "z2": 1.81,
            "valid": False,
            "pointer": None,
        },
        {
            "x1": -4.95,
            "x2": -4.11,
            "z1":  2.09,
            "z2":  2.90,
            "valid": False,
            "pointer": None,
        },
        {
            "x1":  8.37,
            "x2":  9.27,
            "z1": -3.00,
            "z2": -2.50,
            "valid": False,
            "pointer": None,
        }
    ] 
}

all_valid = False

def send_message(address: str, value):
    logging.debug(f"OSC - Broadcasting OSC message - {address}: {value}")
    _client.send_message(address, value)

def on_recieve(*args):
    global all_valid

    if all_valid:
        return

    command, dispatcher_args, x, y, z = args
    pointer = dispatcher_args[0]

    #logging.debug(f"POS - Recieved position for {pointer}: {x}, {z}")

    invalid_position_exists = False

    for position in CONFIG["positions"]:
        if position['x1'] <= x <= position['x2'] and position['z1'] <= z <= position['z2']:
            if position['valid']:
                continue

            logging.debug(f"POS - Position valid for pointer {pointer}: {x}, {z}")

            position['valid'] = True
            position['pointer'] = pointer

            send_message(f'/escaperoom/challenge/3/pos/{pointer}/valid', 1)

        else:
            if position['valid'] and position['pointer'] == pointer:

                logging.debug(f"POS - Position now invalid for pointer {pointer}: {x}, {z}")

                position['valid'] = False
                position['pointer'] = None
                send_message(f'/escaperoom/challenge/3/pos/{pointer}/invalid', 1)

    for position in CONFIG["positions"]:
        if not position['valid']:
            invalid_position_exists = True

    if not invalid_position_exists:
        all_valid = True
        logging.debug('POS - All positions are valid, sending success OSC...')
        send_message(f'/escaperoom/challenge/3/success', 1)


if __name__ == "__main__":
    _dispatcher = dispatcher.Dispatcher()
    _server = osc_server.BlockingOSCUDPServer(('0.0.0.0', 7411), _dispatcher)
    _client = udp_client.SimpleUDPClient('10.100.20.255', 12001, allow_broadcast=True)

    _dispatcher.map('/escape/challenge/3/pos2', on_recieve, 2)
    _dispatcher.map('/escape/challenge/3/pos3', on_recieve, 3)
    _dispatcher.map('/escape/challenge/3/pos4', on_recieve, 4)
    _dispatcher.map('/escape/challenge/3/pos5', on_recieve, 5)
    
    _server.serve_forever()
