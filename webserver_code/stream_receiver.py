import io
import socket
import struct
from PIL import Image
from coffeelvl import GetCoffeeLevel
from coffeePotHistory import generate_graph

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
counter = 0
try:
    while True:
        counter += 1
        print(counter)
        if counter % 50 == 0:
            GetCoffeeLevel()
            print("writing to DB")
            generate_graph()
            print("Generating new graph")
            counter = 1
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        with Image.open(image_stream) as image:

#            print('Image is %dx%d' % image.size)
            #image.verify()
#            print('Image is verified')
            image.save("/var/www/html/image.jpg")

finally:
    connection.close()
    server_socket.close()
