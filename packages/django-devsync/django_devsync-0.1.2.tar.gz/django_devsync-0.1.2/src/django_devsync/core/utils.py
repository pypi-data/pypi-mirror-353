def confirm():
    """
    Prompt the user for a yes/no confirmation.

    Keeps asking until the input is either 'yes' or 'no' (case-insensitive).

    Returns:
        bool: True if user confirms with 'yes', False otherwise.
    """

    while True:
        check = (
            input("Are you sure you want to continue? [yes/no]: ")
            .strip()
            .lower()
        )
        if check in ("yes", "no"):
            return check == "yes"

        print("Please enter 'yes' or 'no'...")
