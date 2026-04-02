import keyboard as kb

while True:
    key = kb.read_key()
    print("{}\n".format(key))
    if key == 'esc':
        break
