import cv2, json

def user_options():
    print("*********************************************")
    print("WELCOME TO THE IMAGE PROCESSING SOFTWARE! :D")
    print("*********************************************")
    print("\nWhat processing would you like to perform on the image?")
    print("     1. Blur faces in a image")
    print("     2. Blur faces under 18")
    print("     3. Draw square in faces")
    print("     4. Draw square in faces")

    option = input("\nSelect an option: ")

    options = {
        '1': lambda: save_new_image("blur"),
        '2': lambda: save_new_image("blur_under_18"),
        '3': lambda: save_new_image("square_face"),
        '4': lambda: save_new_image("apply_labels")
    }

    options.get(option, lambda: invalid_option())()

    # match option:
    #     case '1':
    #         save_new_image("blur")
    #     case '2':
    #         save_new_image("blur_under_18")
    #     case _:
    #         print("\nInvalid option\n")
    #         user_options()


def invalid_option():
    print("\nInvalid option\n")
    user_options()



# Load an image and applies a transformation on the provided option, using information from a JSON file
# Saves the resulting image to the user-specified location
def save_new_image(option):
    image_route = input("Enter the path to the image: ")
    json_route = input("Enter the path to the json file: ")
    save_route = input("Enter the path where you like to save the new image: ")

    # Ensure that the output file has a valid extension
    if not save_route.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        save_route += '.jpg'

    # Load image from specific route
    img = cv2.imread(image_route)
    if img is None:
        print("The image could not be read from the specified path! :(")
        return

    try:
        if option == "blur":
            img = blur_faces(img, json_route)
        elif option == "blur_under_18":
            img = blur_under_18_faces(img, json_route)
        elif option == "square_face":
            img = get_square_on_faces(img, json_route)
        elif option == "apply_labels":
            img = apply_labels_to_image(img, json_route)
        else:
            print("Invalid option selected!")
            return

        # Save the new image in the specific route
        cv2.imwrite(save_route, img)
        print(f"Image successfully saved in --> {save_route}")
    except Exception as e:
        print(f"Error processing image: {e}")



# Applies a blur to faces detected in an image using information from a JSON file
# If a filter is provided, only blurs faces that match the filter condition
def apply_blur_to_faces(image, json_route, filter_18=None):
    with open(json_route, 'r') as file:
        data = json.load(file)

    if "FaceDetails" not in data or not data["FaceDetails"]:
        raise ValueError("Required information was not found in the specified JSON file :(")

    image_height, image_width, _ = image.shape

    for face in data["FaceDetails"]:
        if filter_18 and not filter_18(face):
            continue

        bounding_box = face.get("BoundingBox", {})
        if not bounding_box:
            continue

        # Calculates pixel coordinates based on image size
        x = int(bounding_box["Left"] * image_width)
        y = int(bounding_box["Top"] * image_height)
        width = int(bounding_box["Width"] * image_width)
        height = int(bounding_box["Height"] * image_height)

        # Applies a Gaussian blur to the face region
        face_region = image[y:y + height, x:x + width]
        blurred_face = cv2.GaussianBlur(face_region, (51, 51), 30)
        image[y:y + height, x:x + width] = blurred_face

    return image



# Blur all faces detected in the image
def blur_faces(image, json_route):
    return apply_blur_to_faces(image, json_route)



# Blur only the faces of people under 18 in the image
def blur_under_18_faces(image, json_route):

    def is_under_18(face):
        age_range = face.get("AgeRange", {})
        return age_range.get("Low", 0) < 18

    return apply_blur_to_faces(image, json_route, is_under_18)



# Draw rectangles around faces detected in the image and assign them a color based on age and gender
def get_square_on_faces(image, json_route):
    with open(json_route, 'r') as file:
        data = json.load(file)

    if "FaceDetails" not in data or not data["FaceDetails"]:
        raise ValueError("Required information was not found in the specified JSON file :(")

    image_height, image_width, _ = image.shape

    for face in data["FaceDetails"]:
        bounding_box = face.get("BoundingBox", {})
        if not bounding_box:
            continue

        x = int(bounding_box["Left"] * image_width)
        y = int(bounding_box["Top"] * image_height)
        width = int(bounding_box["Width"] * image_width)
        height = int(bounding_box["Height"] * image_height)

        # Determine the color according to age and gender
        age_range = face.get("AgeRange", {})
        min_age = age_range.get("Low", 0)
        gender = face.get("Gender", {}).get("Value", "Unknown")
        emotions = face.get("Emotions", [])

        if min_age < 18:
            color = (0, 255, 255)
        elif gender == "Male":
             color = (0, 0, 255)
        elif gender == "Female":
            color = (0, 255, 0)
        else:
            color = (255, 255, 255)

        # Draw a rectangle around the face
        cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)


        emotion_text = ""
        if emotions:
            # Sort the emotions by 'Confidence' level and select two highest
            emotions_sorted = sorted(emotions, key=lambda emotion: emotion["Confidence"], reverse=True)[:2]
            emotion_text = ", ".join(f"{e['Type']} ({e['Confidence']:.1f}%)" for e in emotions_sorted)

        # Defines the position of the label
        label_position = (x, y - 10 if y > 20 else y + height + 20)
        cv2.putText(image, emotion_text, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    return image



#
def apply_labels_to_image(image, json_route, save_json):
    return ""