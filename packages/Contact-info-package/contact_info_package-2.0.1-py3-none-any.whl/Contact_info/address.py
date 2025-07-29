# fuction to set address

def set_address(street, city, state, zip_code):
    """
    Function to set the address of the user.
    
    Args:
        street (str): The street address.
        city (str): The city.
        state (str): The state.
        zip_code (str): The zip code.
    
    Returns:
        dict: A dictionary containing the address information.
    """
    address = {
        "street": street,
        "city": city,
        "state": state,
        "zip_code": zip_code
    }
    print("Address set successfully.")
    print(f"Address: {address['street']}, {address['city']}, {address['state']} {address['zip_code']}")

