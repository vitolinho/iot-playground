from muselsl import stream, list_muses


muses = list_muses()

stream(muses[0]["address"], gyro_enabled=True)
