def extract_rich_text(rich_text_list):
    """Helper function to extract plain text from a list of rich text objects."""
    if not rich_text_list:
        return ""
    # Concatenate the 'plain_text' from all parts of the rich text
    return "".join([item.get('plain_text', '') for item in rich_text_list])


def extract_property_value(property_data):
    """
    Extracts the clean value from a single Notion API property object.

    Args:
        property_data (dict): The dictionary representing a single property
                              from the Notion API response (e.g., the value
                              associated with a property name in the 'properties' dict).

    Returns:
        The extracted value in a standard Python type (str, int, float, bool,
        list, dict, or None), or a string indicating an unhandled type.
    """
    prop_type = property_data.get('type')
    if not prop_type:
        # Should not happen in a valid Notion API response
        return None

    # Get the data field corresponding to the property type.
    # This field holds the actual value or further nested structure.
    data_field = property_data.get(prop_type)

    # Handle cases where the data field itself is None (e.g., empty date, empty select)
    if data_field is None:
        # For list types, an empty list is often more useful than None
        if prop_type in ['multi_select', 'relation', 'people', 'files']:
            return []
        # For other types, None means no value
        return None

    # --- Type-specific extraction ---
    # Note: Some types like 'title' and 'rich_text' have the same structure
    if prop_type in ['title', 'rich_text']:
        # These are lists of rich text objects
        return extract_rich_text(data_field)

    elif prop_type == 'number':
        # The value is directly in the 'number' field
        return data_field # This can be int or float, or None (handled above)

    elif prop_type == 'select':
        # The value is a dictionary with 'id', 'name', 'color'. We usually want the name.
        return data_field.get('name') # Returns the name string or None if 'name' is missing

    elif prop_type == 'multi_select':
        # The value is a list of dictionaries, each with 'id', 'name', 'color'.
        # Return a list of names.
        return [item.get('name') for item in data_field if item and item.get('name')]

    elif prop_type == 'status':
         # Similar structure to select
         return data_field.get('name')

    elif prop_type == 'checkbox':
        # The value is a boolean
        return data_field

    elif prop_type == 'date':
        # The value is a dictionary {'start': '...', 'end': '...', 'time_zone': '...'} or None
        # Return the dictionary as is, or None (handled above)
        return data_field

    elif prop_type in ['url', 'email', 'phone_number']:
        # The value is a string or None
        return data_field

    elif prop_type == 'files':
        # The value is a list of file objects. Each object has a 'type' ('external' or 'file')
        # and nested data. We'll extract the URL.
        urls = []
        for file_obj in data_field:
             if file_obj.get('type') == 'external' and 'external' in file_obj:
                 urls.append(file_obj['external'].get('url'))
             elif file_obj.get('type') == 'file' and 'file' in file_obj:
                 urls.append(file_obj['file'].get('url'))
        # Filter out any potential None URLs if extraction failed for an item
        return [url for url in urls if url]

    elif prop_type == 'people':
        # The value is a list of user objects. Each object has 'id', 'name', 'avatar_url', etc.
        # Return a list of names.
        return [person.get('name') for person in data_field if person and person.get('name')]

    elif prop_type == 'relation':
        # The value is a list of dictionaries, each containing the 'id' of the related page.
        # Return a list of relation page IDs.
        return [relation.get('id') for relation in data_field if relation and relation.get('id')]

    elif prop_type == 'formula':
        # The value is a dictionary indicating the formula result type and value.
        formula_result_type = data_field.get('type')
        if formula_result_type in ['string', 'number', 'boolean']:
            return data_field.get(formula_result_type)
        elif formula_result_type == 'date':
            # Formula dates are nested like regular dates
            return data_field.get('date')
        elif formula_result_type == 'array':
             # Array formulas (like rollup results) are complex.
             # Returning the raw array data or attempting recursive extraction
             # might be needed depending on the array content.
             # For simplicity here, let's return the raw array data.
             # A more advanced version might loop through the array and call extract_property_value
             # on each item if they are property-like objects.
             return data_field.get('array')
        elif formula_result_type == 'unsupported':
             return "Unsupported Formula Result"
        else:
             # Handle other potential formula result types if needed
             print(f"Warning: Unhandled formula result type '{formula_result_type}'")
             return None # Or return the raw data_field

    elif prop_type == 'rollup':
        # The value is a dictionary indicating the rollup result type and value.
        rollup_result_type = data_field.get('type')
        # Rollups have different structures based on the function (count, sum, date range, etc.)
        # and the type of the rolled-up property.
        if rollup_result_type in ['number', 'string', 'boolean']:
             # Basic types often have the value directly in the field matching the type
             return data_field.get(rollup_result_type)
        elif rollup_result_type == 'date':
             # Date rollups return a date object
             return data_field.get('date')
        elif rollup_result_type == 'array':
             # Array rollups contain a list of property-like objects from the relation.
             # We can recursively extract values from these items.
             rolled_up_items = data_field.get('array', [])
             # Extract values from each item in the array.
             return [extract_property_value(item) for item in rolled_up_items if item]
        elif rollup_result_type == 'unsupported':
             return "Unsupported Rollup Result"
        # Handle other potential rollup result types/structures as needed
        else:
            print(f"Warning: Unhandled rollup result type '{rollup_result_type}'")
            return None # Or return the raw data_field


    elif prop_type in ['created_time', 'last_edited_time']:
        # These are ISO 8601 date/time strings
        return data_field

    elif prop_type in ['created_by', 'last_edited_by']:
        # These are user objects. We usually want the user's name.
        return data_field.get('name') # Returns name string or None if 'name' is missing

    else:
        # If we encounter a type not explicitly handled
        print(f"Warning: Unhandled property type '{prop_type}'. Returning raw data.")
        return property_data # Or return None, or a specific indicator like f"UNHANDLED_TYPE:{prop_type}"

def transform_notion_properties(properties_data):
    """
    Transforms the 'properties' dictionary from a Notion API page object
    into a clean Python dictionary with property names as keys and extracted
    values as values.

    Args:
        properties_data (dict): The 'properties' dictionary from a Notion API
                                page object response. This is the value associated
                                with the 'properties' key in the full page JSON.

    Returns:
        dict: A dictionary containing property names and their cleaned values.
              Unhandled types will return their raw structure or None depending
              on the extract_property_value implementation.
    """
    cleaned_data = {}
    for prop_name, prop_data in properties_data.items():
        cleaned_data[prop_name] = extract_property_value(prop_data)
    return cleaned_data
