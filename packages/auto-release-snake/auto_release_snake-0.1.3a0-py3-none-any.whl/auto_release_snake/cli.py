

def snake():
    """
    This function returns a string that represents a blue snake in ASCII art.
    """
    return (
        "\033[34m"
        "         __\n"
        "        / _)\n"
        "   _.--._( (_\n"
        "  /  _   \\__)\n"
        " /  (_) _  \\\n"
        " \\_/\\___/\\_/\n"
        "\033[0m" 
    )
if __name__ == "__main__":
    print(snake())
    