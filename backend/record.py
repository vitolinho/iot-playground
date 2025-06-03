from pylsl import StreamInlet, resolve_byprop

# acceleration ACC
# gyroscope GYRO

def record() -> None:
    print("Looking for a GYRO stream...")

    streams = resolve_byprop("type", "GYRO", timeout=1)

    if len(streams) == 0:
        print(f"Can't find GYRO stream.")
        return
    
    inlet = StreamInlet(streams[0], max_chunklen=1)
    
    while True:
        data, _ = inlet.pull_chunk(timeout=1.0, max_samples=1)

        if data != []:
            # ACC PART
            # result = {
            #     "x": round(data[0][0], 2),
            #     "y": round(data[0][1], 2),
            #     "z": round(data[0][2], 2),
            # }

            # print(result)
            
            # GYRO PART

            if data[0][0] > 0 and (data[0][0]>= 20 and data[0][0] <= 90):
                print('GAUCHE')
                continue

            if data[0][0] < 0 and (data[0][0] <= -20 and data[0][0] >= -90):
                print('DROITE')
                continue

            if data[0][1] > 0 and (data[0][1] >= 20 and data[0][1] <= 100):
                print('BAS')
                continue

            if data[0][1] < 0 and (data[0][1] <= -20 and data[0][1] >= -90):
                print('HAUT')
                continue

            result = {
                'x': int(data[0][0]),
                'y': int(data[0][1]),
                'z': int(data[0][2])
            }
            
            print(result)
