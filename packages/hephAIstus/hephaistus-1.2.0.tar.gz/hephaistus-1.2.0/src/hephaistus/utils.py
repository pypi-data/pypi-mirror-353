from os.path import isfile

from pypdf import PdfReader


def read_file(file_name: str):
    """
    Reads the information from a file
    :param file_name:
    str: Location and name of file
    :return:
    str: The extracted text
    """
    # Check that it is a file
    if not isfile(file_name):
        raise ValueError("'{0}' is not a file".format(file_name))

    # Initialize text from file
    text = []

    # Handle PDFs
    if file_name.endswith(".pdf"):
        for page in PdfReader(file_name).pages:
            text.append(page.extract_text())
    # Read file and extract text
    else:
        with open(file_name, "r") as input_file:
            text.append(input_file.read())

    print("Read {0}".format(file_name))
    return "\n".join(text)
