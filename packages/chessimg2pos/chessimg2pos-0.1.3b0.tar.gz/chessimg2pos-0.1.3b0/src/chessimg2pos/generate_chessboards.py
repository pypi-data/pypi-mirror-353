#!/usr/bin/env python3

import os
from io import BytesIO
from urllib import request

import numpy as np
import PIL.Image

# http://www.fen-to-image.com/image/32/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
# http://jinchess.com/chessboard/?p=rnbqkbnrpppppppp--------------------------------PPPPPPPPRNBQKBNR
# https://chessdiagram.online/stilldiagram.php?d=_rnbqkbnrpppppppp________________________________PPPPPPPPRNBQKBNR
# https://chessdiagram.online/stagram.php?d=_rnbqkbnrpppppppp________________________________PPPPPPPPRNBQKBNR
# https://backscattering.de/web-boardimage/board.png?fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR


def generate_random_chessboards(chessboards_dir, n, img_url_template, fen_chars) -> None:
    """Generates n random FEN diagrams from chess diagram template urls and
    saves chessboard images to chessboards_dir

    Output filenames show the pieces at squares from the top-left (a8) to the
    bottom right (h1) of the board, with rows delimited by '-'. For example:

    1bRqBQKq-11RBqkRP-BP1nq1b1-Q1PnkKPq-RPPkKNnr-RKp1pqPB-RRQRPPNQ-k1Ppn1qR.png
    """
    if not os.path.exists(chessboards_dir):
        os.makedirs(chessboards_dir)
    output_dir = os.path.join(chessboards_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i in range(n):
        fen_chars = list(fen_chars)
        fen_arr = np.random.choice(fen_chars, 64)
        if (
            "fen-to-image.com" in img_url_template
            or "backscattering.de" in img_url_template
        ):
            fen_param = "/".join(map("".join, np.split(fen_arr, 8)))
        else:
            fen_param = "".join(fen_arr)
        img_url = img_url_template.format(fen_param)
        print(img_url)
        img = PIL.Image.open(BytesIO(request.urlopen(img_url).read()))
        if "chessdiagram.online" in img_url_template:
            # need to flip FEN file order since the rows are 1-8 vs 8-1 of normal FEN.
            fen_arr = np.hstack(np.split(fen_arr, 8)[::-1])

        # Replace - or _ with 1 to be consistent with actual FEN notation
        fen_arr[fen_arr == fen_chars[0]] = "1"

        # Add '-' between sets of 8 to be consistent with saved file format
        img_filename_prefix = "-".join(map("".join, np.split(fen_arr, 8)))
        file_path = os.path.join(output_dir, img_filename_prefix + ".png")
        print(file_path)
        img.save(file_path)


def jinchess_img_url_template():
    url_template = "http://jinchess.com/chessboard/?p={}"
    jinchess_board_themes = [
        None,
        "cold-marble",
        "gray-tiles",
        "green-marble",
        "pale-wood",
        "red-marble",
        "slate",
        "winter",
        "wooden-dark",
    ]
    jinchess_piece_themes = [
        None,
        "merida-flat",
        "smart-flat",
        "usual-flat",
        "alpha-flat",
    ]
    theme = np.random.choice(jinchess_board_themes, 1)[0]
    if theme is not None:
        url_template += "&bp={}".format(theme)
    pieces = np.random.choice(jinchess_piece_themes, 1)[0]
    if pieces is not None:
        url_template += "&ps={}".format(pieces)
    if np.random.choice(2, 1)[0] == 1:
        url_template += "&gs"
    return url_template