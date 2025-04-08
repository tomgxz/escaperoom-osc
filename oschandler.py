from pythonosc import udp_client, dispatcher, osc_server
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# first position must be smaller than second position
CONFIG:dict = {
    "pos2": {
        "x1": 0,
        "y1": 0,
        "z1": 0,
        "x2": 0,
        "y2": 0,
        "z2": 0,
        "valid": False,
    },
    "pos3": {
        "x1": 0,
        "y1": 0,
        "z1": 0,
        "x2": 0,
        "y2": 0,
        "z2": 0,
        "valid": False,
    },
    "pos4": {
        "x1": 0,
        "y1": 0,
        "z1": 0,
        "x2": 0,
        "y2": 0,
        "z2": 0,
        "valid": False,
    },
    "pos5": {
        "x1": 0,
        "y1": 0,
        "z1": 0,
        "x2": 0,
        "y2": 0,
        "z2": 0,
        "valid": False,
    }
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
    pos = dispatcher_args[0]
    cfg = CONFIG[f"pos{pos}"]


    if cfg['x1'] <= x <= cfg['x2'] and cfg['y1'] <= y <= cfg['y2'] and cfg['z1'] <= z <= cfg['z2']:
        if cfg['valid']:
            return
        
        cfg['valid'] = True
        send_message(f'/escaperoom/challenge/3/pos/{pos}/valid')

        if CONFIG["pos2"]["valid"] and CONFIG["pos3"]["valid"] and CONFIG["pos4"]["valid"] and CONFIG["pos5"]["valid"]:
            all_valid = True

            logging.debug('All positions are valid, sending success OSC...')
            send_message(f'/escaperoom/challenge/3/success')

    else:
        if not cfg['valid']:
            return
        
        cfg['valid'] = False
        send_message(f'/escaperoom/challenge/3/pos/{pos}/invalid')

    logging.debug(f"Recieved position for {pos}: {x}, {y}, {z} - valid = {cfg}")


if __name__ == "__main__":
    _dispatcher = dispatcher.Dispatcher()
    _server = osc_server.BlockingOSCUDPServer(('0.0.0.0', 7411), _dispatcher)
    _client = udp_client.SimpleUDPClient('10.100.20.255', 12001, allow_broadcast=True)

    _dispatcher.map('/escape/challenge/3/pos2', on_recieve, 2)
    _dispatcher.map('/escape/challenge/3/pos3', on_recieve, 3)
    _dispatcher.map('/escape/challenge/3/pos4', on_recieve, 4)
    _dispatcher.map('/escape/challenge/3/pos5', on_recieve, 5)
    
    _server.serve_forever()