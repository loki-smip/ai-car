import qrcode
from PIL import Image

# Function to generate QR code with a specific data string
def generate_qr_code(data, filename):
    # Create a QR code from the data string
    qr = qrcode.QRCode(
        version=1,  # Version of the QR code (1 is the smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Size of each box in the QR code grid
        border=4,  # Thickness of the border around the QR code
    )
    qr.add_data(data)  # Add the data string to the QR code
    qr.make(fit=True)  # Fit the QR code to the size

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Save the image
    img.save(filename)

# Generate QR codes for the car and the target
def generate_car_and_target_qr_codes():
    # QR Code for the car
    car_data = "car"  # The identifier for the car
    car_filename = "car_qr.png"
    generate_qr_code(car_data, car_filename)
    print(f"Car QR Code generated and saved as {car_filename}")

    # QR Code for the target (object)
    target_data = "target"  # The identifier for the target object
    target_filename = "target_qr.png"
    generate_qr_code(target_data, target_filename)
    print(f"Target QR Code generated and saved as {target_filename}")

# Main function to generate the QR codes
if __name__ == '__main__':
    generate_car_and_target_qr_codes()
