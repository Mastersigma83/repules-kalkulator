# Mavic 3 Multispectral Camera Parameters (Updated)

# RGB Camera
RGB_FOCAL_LENGTH_MM = 24.5
RGB_IMAGE_WIDTH_PX = 5280
RGB_SENSOR_WIDTH_MM = 17.3

# Multispectral Camera
MULTI_FOCAL_LENGTH_MM = 4.7
MULTI_IMAGE_WIDTH_PX = 2592  # Updated from 1600 to 2592
MULTI_SENSOR_WIDTH_MM = 6.4

# Function to calculate GSD

def calculate_gsd(flight_altitude_m, focal_length_mm, sensor_width_mm, image_width_px):
    # Convert altitude from meters to millimeters
    flight_altitude_mm = flight_altitude_m * 1000
    gsd_mm_per_px = (flight_altitude_mm * sensor_width_mm) / (focal_length_mm * image_width_px)
    gsd_cm_per_px = gsd_mm_per_px / 10
    return gsd_cm_per_px

# Example calculation at 90 meters
flight_altitude_m = 90

rgb_gsd = calculate_gsd(
    flight_altitude_m,
    RGB_FOCAL_LENGTH_MM,
    RGB_SENSOR_WIDTH_MM,
    RGB_IMAGE_WIDTH_PX
)

multi_gsd = calculate_gsd(
    flight_altitude_m,
    MULTI_FOCAL_LENGTH_MM,
    MULTI_SENSOR_WIDTH_MM,
    MULTI_IMAGE_WIDTH_PX
)

print(f"RGB camera GSD at {flight_altitude_m}m: {rgb_gsd:.2f} cm/px")
print(f"Multispectral camera GSD at {flight_altitude_m}m: {multi_gsd:.2f} cm/px")
