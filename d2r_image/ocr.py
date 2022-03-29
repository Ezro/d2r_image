from tesserocr import PyTessBaseAPI, OEM
import numpy as np
import cv2
import re
import difflib
from d2r_image.utils.misc import erode_to_black
import logging
from typing import List, Union
from d2r_image.data_models import OcrResult
import os
import shutil
import pkgutil
from d2r_image.ocr_data import TrainedDataSets, OCR_WORKING_DIR, ERROR_RESOLUTION_MAP, I_1, II_U, One_I, OneOne_U, OCR_CONFIG
from rapidfuzz.process import extractOne
from rapidfuzz.string_metric import levenshtein


if os.path.exists(OCR_WORKING_DIR):
    shutil.rmtree(OCR_WORKING_DIR)
os.mkdir(OCR_WORKING_DIR)
for trained_data in TrainedDataSets:
    trained_data_path = os.path.join(
        OCR_WORKING_DIR, f'{trained_data.value}.traineddata')
    file = open(trained_data_path, 'wb')
    trained_data = pkgutil.get_data(
        __name__,
        f"resources/tessdata/{trained_data.value}.traineddata")
    file.write(bytearray(trained_data))
_word_list_data = pkgutil.get_data(
    __name__,
    f"resources/tessdata/word_lists/all_strings.txt")
word_list = _word_list_data.decode()
word_list_path = os.path.join(OCR_WORKING_DIR, 'all_strings.txt')
file = open(word_list_path, 'wb')
file.write(bytearray(word_list, encoding='utf-8'))
file.close()


def image_to_text(
    images: Union[np.ndarray, List[np.ndarray]],
    model: str = "engd2r_inv_th",
    psm: int = 3,
    word_list: str = word_list,
    scale: float = 1.0,
    crop_pad: bool = True,
    erode: bool = True,
    invert: bool = True,
    threshold: int = 25,
    digits_only: bool = False,
    fix_regexps: bool = True,
    check_known_errors: bool = True,
    check_wordlist: bool = True,
    word_match_threshold: float = 0.5
) -> list[str]:
    """
    Uses Tesseract to read image(s)
    :param images (required): image or list of images to read in OpenCV format.
        Use a list of images rather than looping over single images where possible for best performance.
    :param model: OCR language model basename to use (in d2r_image/tessdata folder)
    :param psm: Tesseract PSM to use. 7=single uniform text line, 6=single block of text, 3=auto without orientation.
        See https://www.pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/
    :param word_list: predefined wordlist to use. Tesseract will use these to help with recognition
    :param scale: scales input image, sometimes necessary for smaller text (but doesn't always improve accuracy). Engd2r_inv_th trained on ~1.6x scaled assets.
    :param crop_pad: crop the outer part and then re-pad image. Intended for item drops.
    :param erode: use erosion function to erode image to black borders (i.e. for item drops)
    :param invert: invert and threshold the input image(s)
    :param threshold: apply threshold to image (ex. 25 would threshold around V=25). Set to 0 to not threshold image.
    :param digits_only: only look for digits
    :param fix_regexps: use regex for various cases of common errors (I <-> 1, etc.)
    :param check_known_errors: check for predefined common errors and replace
    :param check_wordlist: check dictionary of words and match closest match if proximity is greater than word_match_threshold
    :param word_match_threshold: (see check_wordlist)
    :return: Returns an OcrResult object
    """
    if type(images) == np.ndarray:
        images = [images]
    results = []
    api = PyTessBaseAPI(
        psm=psm,
        oem=OEM.LSTM_ONLY,
        path=OCR_WORKING_DIR,
        lang=model)
    api.ReadConfigFile(OCR_CONFIG)
    api.SetVariable("user_words_file", "all_strings.txt")
    #api.SetSourceResolution(72 * scale)
    for image in images:
        processed_img = image
        if scale:
            processed_img = cv2.resize(
                processed_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        if erode:
            processed_img = erode_to_black(processed_img)
        if crop_pad:
            processed_img = _crop_pad(processed_img)
        image_is_binary = (image.shape[2] if len(
            image.shape) == 3 else 1) == 1 and image.dtype == bool
        if not image_is_binary and threshold:
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
            processed_img = cv2.threshold(
                processed_img, threshold, 255, cv2.THRESH_BINARY)[1]
        if invert:
            if threshold or image_is_binary:
                processed_img = cv2.bitwise_not(processed_img)
            else:
                processed_img = ~processed_img
        api.SetImageBytes(*_img_to_bytes(processed_img))
        if digits_only:
            api.SetVariable("tessedit_char_blacklist",
                            ".,!?@#$%&*()<>_-+=/:;'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            api.SetVariable("tessedit_char_whitelist", "0123456789")
            api.SetVariable("classify_bln_numeric_mode", "1")
        original_text = api.GetUTF8Text()
        text = original_text
        # replace newlines if image is a single line
        if psm in (7, 8, 13):
            text = text.replace('\n', '')
        word_confidences = api.AllWordConfidences()
        if fix_regexps:
            text = _fix_regexps(text)
        if check_known_errors:
            text = _check_known_errors(text)
        if check_wordlist and any([x <= 90 for x in word_confidences]):
            text = _check_wordlist(
                text, word_list, word_confidences, word_match_threshold)
            text = text.replace(' NEWLINEHERE ', '\n')
        results.append(OcrResult(
            original_text=original_text,
            text=text,
            word_confidences=word_confidences,
            mean_confidence=api.MeanTextConf()
        ))
    return results


def _crop_pad(image: np.ndarray = None):
    # crop
    image = image[4: image.shape[0]-4, 5: image.shape[1]-5]
    # re-pad
    image = np.pad(image, pad_width=[(4, 4), (4, 4), (0, 0)], mode='constant')
    return image


def _img_to_bytes(image: np.ndarray, colorspace: str = 'BGR'):
    # Sets an OpenCV-style image for recognition: https://github.com/sirfz/tesserocr/issues/198
    bytes_per_pixel = image.shape[2] if len(image.shape) == 3 else 1
    height, width = image.shape[:2]
    bytes_per_line = bytes_per_pixel * width
    if bytes_per_pixel != 1 and colorspace != 'RGB':
        # non-RGB color image -> convert to RGB
        image = cv2.cvtColor(image, getattr(cv2, f'COLOR_{colorspace}2RGB'))
    elif bytes_per_pixel == 1 and image.dtype == bool:
        # binary image -> convert to bitstream
        image = np.packbits(image, axis=1)
        bytes_per_line = image.shape[1]
        width = bytes_per_line * 8
        bytes_per_pixel = 0
    # else image already RGB or grayscale
    return image.tobytes(), width, height, bytes_per_pixel, bytes_per_line


def _fix_regexps(ocr_output: str, repeat_count: int = 0) -> str:
    # case: two 1's within a string; e.g., "SIIPER MANA POTION"
    try:
        text = II_U.sub('U', ocr_output)
    except:
        # logging.error(f"Error _II_ -> _U_ on {ocr_output}")
        text = ocr_output
    # case: two 1's within a string; e.g., "S11PER MANA POTION"
    try:
        text = OneOne_U.sub('U', text)
    except:
        # logging.error(f"Error _11_ -> _U_ on {ocr_output}")
        pass
    # case: an I within a number or by a sign; e.g., "+32I to mana attack rating"
    try:
        text = I_1.sub('1', text)
    except:
        # logging.error(f"Error I -> 1 on {ocr_output}")
        pass
    # case: a 1 within a string; e.g., "W1RT'S LEG"
    try:
        text = One_I.sub('I', text)
    except:
        # logging.error(f"Error 1 -> I on {ocr_output}")
        pass
    # case: a solitary I; e.g., " I TO 5 DEFENSE"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error ' I ' -> ' 1 ' on {ocr_output}")
            break
        if " I " in text:
            text = text.replace(" I ", " 1 ")
            continue
        elif ' I\n' in text:
            text = text.replace(' I\n', ' 1\n')
            continue
        elif '\nI ' in text:
            text = text.replace('\nI ', '\n1 ')
            continue
        break
    # case: a solitary S; e.g., " 1 TO S DEFENSE"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error ' S ' -> ' 5 ' on {ocr_output}")
            break
        if " S " in text:
            text = text.replace(" S ", " 5 ")
            continue
        elif ' I\n' in text:
            text = text.replace(' S\n', ' 5\n')
            continue
        elif '\nI ' in text:
            text = text.replace('\nS ', '\n5 ')
            continue
        break
    # case: consecutive I's; e.g., "DEFENSE: II"
    repeat = False
    cnt = 0
    while "II" in text:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error 4 on {ocr_output}")
            break
        text = text.replace("II", "11")
        repeat = True
        repeat_count += 1
    if repeat and repeat_count < 10:
        _fix_regexps(text)
    return text


def _check_known_errors(text):
    for key in ERROR_RESOLUTION_MAP:
        if key in text:
            text = text.replace(key, ERROR_RESOLUTION_MAP[key])
    return text


def _check_wordlist(text: str = None, word_list: str = None, confidences: list = [], match_threshold: float = 0.5) -> str:
    word_count = 0
    new_string = ""
    text = text.replace('\n', ' NEWLINEHERE ')
    for word in word_list:
        try:
            if confidences[word_count] <= 90:
                alphanumeric = re.sub(r"[^a-zA-Z0-9]", "", word)
                if not alphanumeric.isnumeric() and (word not in word_list) and alphanumeric not in word_list:
                    closest_match, similarity, _ = extractOne(word, word_list, scorer=levenshtein)
                    normalized_similarity = 1 - similarity / len(word)
                    if (normalized_similarity) >= (match_threshold):
                        new_string += f"{closest_match} "
                        # logging.debug(
                        #     f"check_wordlist: Replacing {word} ({confidences[word_count]}%) with {closest_match}, similarity={normalized_similarity*100:.1f}%")
                    else:
                        new_string += f"{word} "
                else:
                    new_string += f"{word} "
            else:
                new_string += f"{word} "
            word_count += 1
        except IndexError:
            # bizarre word_count index exceeded sometimes... can't reproduce and words otherwise seem to match up
            # logging.error(
            #     f"check_wordlist: IndexError for word: {word}, index: {word_count}, text: {text}")
            return text
        except Exception as e:
            # logging.error(
            #     f"check_wordlist: Unknown error for word: {word}, index: {word_count}, text: {text}, exception: {e}")
            return text
    return new_string.strip()