import cv2

# Function to load an image
def load_image(image_route_in):
    image = cv2.imread(image_route_in)

    if image is None:
        raise ValueError("Image not found!")

    return image

# Function to process an image
def process_image(image_route_in, image_route_out, action):
    image = cv2.imread(image_route_in)

    if image is None:
        raise ValueError("Image not found!")

    image_processed = action(image)
    cv2.imwrite(image_route_out, image_processed)

# Function to rotate an image 180º and generate a new one
def rotate_180_image(image_route_in, image_route_out):
    return process_image(image_route_in, image_route_out, lambda image: cv2.rotate(image, cv2.ROTATE_180))

# Function to generate a negative color image
def get_negative_colors(image_route_in, image_route_out):
    return process_image(image_route_in, image_route_out, cv2.bitwise_not)

# Function to generate a gray scale image
def get_gray_scale(image_route_in, image_route_out):
    return process_image(image_route_in, image_route_out, lambda image: cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

# Function to generate a square from two coordinates
def get_rectangle_with_coordinates(image_route_in, image_route_out, x_coordinates, y_coordinates, color):
    return process_image(image_route_in, image_route_out, lambda image: cv2.rectangle(image, x_coordinates, y_coordinates, color, 2))

# Function to generate a new image that invert the colors inside the square box
def get_invert_color_inside_square(image_route_in, image_route_out, x_coordinates, y_coordinates):
    return process_image(image_route_in, image_route_out, lambda image: cv2.bitwise_not(image, x_coordinates, y_coordinates))  # Fix error

# Function to generate a new image to avoid dimensions with odd values
def get_image_without_odd_values(image_route_in, image_route_out):

    def dimensions(image):
        height, weight = image.shape[:2]
        new_height = height if height % 2 == 0 else height - 1
        new_weight = weight if weight % 2 == 0 else weight - 1

        return image[:new_height, :new_weight]

    return process_image(image_route_in, image_route_out, dimensions)

# Function to generate a new mirror-image
def get_mirror_image(image_route_in, image_route_out):
    return process_image(image_route_in, image_route_out, lambda image: cv2.flip(image, 1))

# Function to generate an invert the left half and copy it to the right
def get_inverted_image(image_route_in, image_route_out, type):

    def invert_vertical_image(image):
        height, width, _ = image.shape
        half = width // 2
        image_inverted = cv2.flip(image[:, :half], 1)
        image[:, half:] = image_inverted

        return image

    def invert_horizontal_image(image):
        height, width, _ = image.shape
        half = height // 2
        image_inverted = cv2.flip(image[:half, :], 0)
        image[half:, :] = image_inverted

        return image

    if type == 'vertical':
        return process_image(image_route_in, image_route_out, invert_vertical_image)
    elif type == 'horizontal':
        return process_image(image_route_in, image_route_out, invert_horizontal_image)
    else:
        raise ValueError(f"Invalid type: {type}. Choose between 'vertical' or 'horizontal'")


# Function to generate an HTML document where it shows the original image and the ones which where generated in
# 'get_inverted_image' and 'get_mirror_image'
def generate_html_file(image_route_in, image_route_out, html_out):
    with open(html_out, 'w') as file:
        mirror_image = get_mirror_image(image_route_in, image_route_out)
        vertical_image = get_inverted_image(image_route_in, image_route_out, 'vertical')
        horizontal_image = get_inverted_image(image_route_in, image_route_out, 'horizontal')

        file.write(f"""
        <html>
            <body>
                <table border = "1">
                    <tr>
                        <th>Original</th>
                        <th>Espejo</th>
                        <th>Vertical</th>
                        <th>Horizontal</th>
                    </tr>
                    <tr>
                        <td><img src="{image_route_in}" width="200"></td>
                        <td><img src="{mirror_image}" width="200"></td>
                        <td><img src="{vertical_image}" width="200"></td>
                        <td><img src="{horizontal_image}" width="200"></td>
                    </tr>
                </table>
            </body>
        </html>
        """)


# Function to generate a box in the image with a text
def get_image_with_text(image_route_in, image_route_out, x_coordinates, y_coordinates, color, text):
    def image_with_text(image):
        cv2.rectangle(image, x_coordinates, y_coordinates, color, 2)
        x, y = y_coordinates
        cv2.putText(image, text, (x - 475, y - 30), cv2.FONT_ITALIC, 3, color, 2)

        return image

    process_image(image_route_in, image_route_out, image_with_text)


# Function to generate an image with a specific area blurred
def blur_action(image, x_coordinates, y_coordinates):

    x1, x2 = x_coordinates
    y1, y2 = y_coordinates

    image[y1:y2, x1:x2] = cv2.medianBlur(image[y1:y2, x1:x2], 99)

    return image

def get_image_blurred(image_route_in, image_route_out, x_coordinates, y_coordinates):
    process_image(image_route_in, image_route_out, lambda image: blur_action(image, x_coordinates, y_coordinates))


def detect_and_mark_faces(image_route_in, image_route_out, color,  text, blur_faces=False):
    image = load_image(image_route_in)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces = face.detectMultiScale(gray_image, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

        if blur_faces:
            face = image[y:y+h, x:x+w]
            face_blurred = cv2.medianBlur(face, 99)
            image[y:y+h, x:x+w] = face_blurred

        if text:
            cv2.putText(image, text, (x - 475, y - 30), cv2.FONT_ITALIC, 0.9, color, 2, cv2.LINE_AA)

    return cv2.imwrite(image_route_out, image)

def webcam_face_eyes():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    if face_cascade.empty(): raise Exception("¿Está seguro que es la ruta correcta?")
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    if eye_cascade.empty(): raise Exception("¿Está seguro que es la ruta correcta?")
    video = cv2.VideoCapture(0)
    while video.isOpened():
        ret, frame = video.read()
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

def webcam_blur_face():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    if face_cascade.empty(): raise Exception("¿Está seguro que es la ruta correcta?")
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    if eye_cascade.empty(): raise Exception("¿Está seguro que es la ruta correcta?")
    video = cv2.VideoCapture(0)
    while video.isOpened():
        ret, frame = video.read()
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                # Extraer región de la cara
                rostro = frame[y:y + h, x:x + w]
                # Aplicar un desenfoque Gaussian
                rostro_blur = cv2.GaussianBlur(rostro, (99, 99), 30)
                # Reemplazar la región original con la desenfocada
                frame[y:y + h, x:x + w] = rostro_blur
            cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()