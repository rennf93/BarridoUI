import unicodedata
import re


def clean_string(source_string, array_of_chars_to_replace) -> str:
    unicodedata.normalize('NFKD', source_string).encode('ascii', 'ignore')
    regex = re.compile(r".\s\s+")
    source_string = re.sub(regex, "", source_string)
    return multiple_replace(source_string, array_of_chars_to_replace, '')


def multiple_replace(source_string, array_of_chars, target_char):
    for char in array_of_chars:
        source_string = source_string.replace(char, target_char)
    return source_string
