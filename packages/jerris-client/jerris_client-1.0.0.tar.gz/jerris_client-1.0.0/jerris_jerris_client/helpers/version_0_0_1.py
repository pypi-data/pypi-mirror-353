from jerris_jerris_client.const.parameters import PARAMETERS_MAPPING


def v0_1_0_get_id(parameter: str) -> int | None:
    if parameter in PARAMETERS_MAPPING:
        return PARAMETERS_MAPPING[parameter].get("id")
    return None


def v0_1_0_get_title(parameter: str) -> str | None:
    if parameter in PARAMETERS_MAPPING:
        return PARAMETERS_MAPPING[parameter].get("title")
    return None


def v0_1_0_get_title_v1_0_0(v0_1_0_title: str) -> str:
    title = v0_1_0_title.strip('"').strip()

    # Manual mapping
    if title == "AI Creation Probabiltiy" or title == "AI Creation Probability":
        # Typo
        return "Artificial Intelligence Creation Probability"
    elif title == "ColorMode":
        # Missing space
        return "Color Mode"
    elif title == "HDR (High Dynamic Range)" or title.upper() == "HDR":
        # Missing space
        return "High Dynamic Range"
    elif (
        title.lower() == "highlight textures and details to add depth and interest."
        or title.lower() == "highlight textures and details to add depth and interest"
    ):
        # Trailing dot and space
        return "Highlight Textures and Details"

    return title


def v0_1_0_get_name_v1_0_0(v0_1_0_title: str) -> str:
    return v0_1_0_get_title_v1_0_0(v0_1_0_title).lower().replace(" ", "-")
