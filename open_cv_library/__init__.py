from open_cv_library.images import (
    rotate_180_image, get_negative_colors, get_gray_scale, get_rectangle_with_coordinates,
    get_invert_color_inside_square, get_image_without_odd_values, get_mirror_image,
    get_inverted_image, generate_html_file, get_image_with_text, get_image_blurred,
    detect_and_mark_faces, process_webcam
)
from resources.resources import A, A_final, A_vertical, A_horizontal, A_mirror, B, B_final, A_html, f2, f2_final

# rotate_180_image(f1, f1_rotated)
# get_negative_colors(f2, f2_negative)
# get_gray_scale(f1, f1_gray)
# get_rectangle_with_coordinates(f2, f2_rectangle, (1500,250), (2000,800), (0, 0, 255))
# get_invert_color_inside_square(m2, m2_invcua, [400, 500], [500, 600])
# get_image_without_odd_values(m1, m1_par)
# get_mirror_image(m2, m2_mirror)
# get_inverted_image(m2, m2_inverted, 'vertical')
# get_inverted_image(m2, m2_inverted, 'horizontal')
# generate_html_file(m2, m2_prueba, m2_html)
# get_image_with_text(f2, f2_rectangle_text, (1500, 250), (2000, 800), (0, 0, 255), "Ana")
# get_image_blurred(f2, f2_final, (1500, 2000), (250, 800))
# detect_and_mark_faces(g1, g1_detected)
# process_webcam(operation="face_and_eyes")
# process_webcam(operation="blur_face")