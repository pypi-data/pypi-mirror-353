from datetime import datetime, timezone

from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.realtime_api.streaming.eye_events import (
    BlinkEventData,
    FixationEventData,
)

# Look for devices. Returns as soon as it has found the first device.
print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    print("No device found.")
    raise SystemExit(-1)

# device.streaming_start()  # optional, if not called, stream is started on-demand

try:
    while True:
        eye_event = device.receive_eye_events()
        if isinstance(eye_event, BlinkEventData):
            time_sec = eye_event.start_time_ns // 1e9
            blink_time = datetime.fromtimestamp(time_sec, timezone.utc)
            print(f"[BLINK] blinked at {blink_time.strftime('%H:%M:%S')} UTC")

        elif isinstance(eye_event, FixationEventData) and eye_event.event_type == 0:
            angle = eye_event.amplitude_angle_deg
            print(f"[SACCADE] event with {angle:.0f}° amplitude.")

        elif isinstance(eye_event, FixationEventData) and eye_event.event_type == 1:
            duration = (eye_event.end_time_ns - eye_event.start_time_ns) / 1e9
            print(f"[FIXATION] event with duration of {duration:.2f} seconds.")

        # print(eye_event) # This will print all the fields of the eye event

except KeyboardInterrupt:
    pass

finally:
    print("Stopping...")
    # device.streaming_stop()  # optional, if not called, stream is stopped on close
    device.close()  # explicitly stop auto-update
