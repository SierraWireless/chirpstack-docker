#!/usr/bin/env python3

# Value used for the conversion of the position from DMS to decimal
MaxNorthPosition = 8388607 # 2^23 - 1
MaxSouthPosition = 8388608 # -2^23
MaxEastPosition = 8388607 # 2^23 - 1
MaxWestPosition = 8388608 # -2^23

#test
# data = "0000003D05017805" # 0 ok
# data = "FFFF7F3D05017805" # +90 ok
# data = "0000803D05017805" # -90 ok
data = "7CF3C13D05017805" # -43.6281286 KO
print("Uplink received payload: %s" % (data))

# Decode Latitude and Longitude from Data Payload
latitude = int(data[0:2], 16) + (int(data[2:4], 16) << 8) + (int(data[4:6], 16) << 16)

# We want a signed int
if int(data[4:6], 16) & 0x80:
    latitude = -((latitude - 1) ^ 0xffffff)

if latitude < 0:
    # Negative => South latitude
    latitude = latitude * 90 / MaxSouthPosition
else:
    # Positive => North latitude
    latitude = latitude * 90 / MaxNorthPosition

print(latitude)