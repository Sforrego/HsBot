from PIL import Image
import numpy as np


def read_image(path):
    try:
        image = Image.open(path)
        return image
    except Exception as e:
        print(e)

def paint_tiles(tiles):

    img_path = "Bingo_board2.png"
    image = read_image(img_path)
    img_array = np.array(image)

    for tile in tiles:
        for i in range(tile//5*76, (tile//5)*76+75):
            for j in range(tile%5*92, (tile%5)*91+90):

                img_array[i][j] = np.array([0,200, 0, 255])
    return Image.fromarray(img_array)


if __name__ == '__main__':
    image = paint_tiles([1,3,7,15,18,24])
    image.save('team1.png')
