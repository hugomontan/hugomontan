import datetime
from dateutil import relativedelta
from lxml import etree


def calculate_uptime(birthday):
    """
    Calculate uptime since the given birthday.
    """
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} years, {} months, {} days'.format(diff.years, diff.months, diff.days)


def edit_svg(file_name, new_name, uptime, programming_languages, real_languages, interests):
    """
    Edit the SVG file with the provided updates.
    """
    # Parse the SVG file
    tree = etree.parse(file_name)
    root = tree.getroot()

    # Update the header name
    find_and_replace(root, "header_name", new_name)

    # Update the uptime
    find_and_replace(root, "age_data", uptime)

    # Remove Host, Kernel, and IDE
    remove_element_by_id(root, "host")
    remove_element_by_id(root, "kernel")
    remove_element_by_id(root, "ide")

    # Update programming languages
    find_and_replace(root, "languages_programming", programming_languages)

    # Update real languages
    find_and_replace(root, "languages_real", real_languages)

    # Update interests
    find_and_replace(root, "interests", interests)

    # Fix line breaks between Interests and Contact
    adjust_spacing(root, "interests", "contact", single_break=True)

    # Remove line break between Email.Personal and Email.Work
    merge_elements(root, "email_personal", "email_work")

    # Save the updated SVG
    tree.write("updated_" + file_name, encoding='utf-8', xml_declaration=True)


def find_and_replace(root, element_id, new_text):
    """
    Finds the element in the SVG by ID and replaces its text.
    """
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text


def remove_element_by_id(root, element_id):
    """
    Remove an element by ID from the SVG tree.
    """
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.getparent().remove(element)


def adjust_spacing(root, first_element_id, second_element_id, single_break=False):
    """
    Adjust spacing between two elements by ID.
    If `single_break` is True, ensures there is only one line of spacing.
    """
    first_element = root.find(f".//*[@id='{first_element_id}']")
    second_element = root.find(f".//*[@id='{second_element_id}']")
    if first_element is not None and second_element is not None:
        if single_break:
            second_element.attrib["y"] = str(float(first_element.attrib["y"]) + 20)  # Adjust spacing as needed


def merge_elements(root, first_element_id, second_element_id):
    """
    Merge two elements into one line by adjusting their coordinates.
    """
    first_element = root.find(f".//*[@id='{first_element_id}']")
    second_element = root.find(f".//*[@id='{second_element_id}']")
    if first_element is not None and second_element is not None:
        first_element.text += " | " + second_element.text
        second_element.getparent().remove(second_element)


if __name__ == "__main__":
    # Inputs for the new SVG configuration
    birthday = datetime.datetime(2004, 12, 15)
    uptime = calculate_uptime(birthday)

    # Call the SVG editor with updated values
    edit_svg(
        file_name="profile.svg",
        new_name="hugo.montan",
        uptime=uptime,
        programming_languages="Python, R",
        real_languages="Portuguese, English",
        interests="Finance, Crypto, Politics",
    )

    print("SVG updated successfully!")
