import cv2

# Function to load an image
def load_image(image_route_in):
    image = cv2.imread(image_route_in)

    if image is None:
        raise ValueError("Image not found!")

    return image

# Function to process an image
def process_image(image_route_in, image_route_out, action):
    image = load_image(image_route_in)

    if image is None:
        raise ValueError("Image not found!")

    image_processed = action(image)
    cv2.imwrite(image_route_out, image_processed)

    return image_route_out

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
def get_rectangle_with_coordinates(image_route_in, image_route_out, first_coordinate, second_coordinate, color):
    return process_image(image_route_in, image_route_out, lambda image: cv2.rectangle(image, first_coordinate, second_coordinate, color, 2))

# Function to generate a new image that invert the colors inside the square box
def get_invert_color_inside_square(image_route_in, image_route_out, first_coordinate, second_coordinate):
    return process_image(image_route_in, image_route_out, lambda image: cv2.bitwise_not(image, first_coordinate, second_coordinate))  # Fix error

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

    inverted_path = image_route_out.replace(".jpg", f"_{type}.jpg")

    def invert_vertical_image(image):
        height, width, _ = image.shape
        half = width // 2
        image_inverted = cv2.flip(image[:, :half], 1)
        image[:, half:] = image_inverted

        return image

    def invert_horizontal_image(image):
        height, width, _ = image.shape
        half = height // 2

        if height % 2 == 0:
            image_inverted = cv2.flip(image[:half, :], 0)
        else:
            image_inverted = cv2.flip(image[:half + 1, :], 0)


        image[half:, :] = image_inverted[:height - half, :]

        return image

    if type == 'vertical':
        result = process_image(image_route_in, image_route_out, invert_vertical_image)
    elif type == 'horizontal':
        result =  process_image(image_route_in, image_route_out, invert_horizontal_image)
    else:
        raise ValueError(f"Invalid type: {type}. Choose between 'vertical' or 'horizontal'")

    return inverted_path if result else None


# Function to generate an HTML document where it shows the original image and the ones which where generated in
# 'get_inverted_image' and 'get_mirror_image'
def generate_html_file(image_route_in, mirror_image_out, vertical_image_out, horizontal_image_out, html_out):
    with open(html_out, 'w') as file:
        mirror_image = get_mirror_image(image_route_in, mirror_image_out)
        vertical_image = get_inverted_image(image_route_in, vertical_image_out, 'vertical')
        horizontal_image = get_inverted_image(image_route_in, horizontal_image_out, 'horizontal')

        file.write(f"""
        <!DOCTYPE html>
        <html lang="en">
            <body>
                <table border = "1">
                    <tr>
                        <th>Original</th>
                        <th>Espejo</th>
                        <th>Vertical</th>
                        <th>Horizontal</th>
                    </tr>
                    <tr>
                        <td><img src="{image_route_in}" width="400"></td>
                        <td><img src="{mirror_image}" width="400"></td>
                        <td><img src="{vertical_image}" width="400"></td>
                        <td><img src="{horizontal_image}" width="400"></td>
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

    return process_image(image_route_in, image_route_out, image_with_text)


# Function to generate an image with a specific area blurred
def blur_action(image, first_coordinate, second_coordinate):

    x1, x2 = first_coordinate
    y1, y2 = second_coordinate

    image[y1:y2, x1:x2] = cv2.GaussianBlur(image[y1:y2, x1:x2], (99, 99), 0)

    return image


# Function that applies a blur to a specific region of the image
def get_image_blurred(image_route_in, image_route_out, x_coordinates, y_coordinates):
    return process_image(image_route_in, image_route_out, lambda image: blur_action(image, x_coordinates, y_coordinates))


# Function that detects faces in an image, marks them with a rectangle and optionally blurs them
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


# Load the cascade classifier to detect faces and eyes
def get_classifier(cascade_route):
    cascade = cv2.CascadeClassifier(cascade_route)

    if cascade.empty():
        raise Exception (f"Error loading classifier from {cascade_route}!")

    return cascade


# Function that starts capturing video from the webcam
def capture_video():
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        raise Exception("The camera cannot be accessed! :/")

    return video


# Function that detects faces and eyes in a frame and draws rectangles around them
def get_face_and_eyes_from_webcam(frame, face_cascade, eye_cascade):

    faces = face_cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.3, 5)

    for (x, y, w, h) in faces:
        # Rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Detect eyes
        roi_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    return frame


# Function that detects faces and blur them
def get_blur_face_from_webcam(frame, face_cascade):
    faces = face_cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.3, 5)

    for (x, y, w, h) in faces:
        face = frame[y:y + h, x:x + w]
        face_blurred = cv2.GaussianBlur(face, (99,99), 30)
        frame[y:y + h, x:x + w] = face_blurred

    return frame


# Processes the live video from the camera according to the selected operation
def process_webcam(operation):
    face_cascade = get_classifier('haarcascade_frontalface_default.xml')
    eye_cascade = get_classifier('haarcascade_eye.xml')

    video = capture_video()

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        if operation == "face_and_eyes":
            frame = get_face_and_eyes_from_webcam(frame, face_cascade, eye_cascade)
        elif operation == "blur_faces":
            frame = get_blur_face_from_webcam(frame, face_cascade)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()