def left_string(string, padding):
    """
    Formats a string with padding. Either adds spaces to the end or truncates

    Args
    ----
    string : str
        String for printing
    padding : int
        Width (in columns) for the final format

    Returns
    -------
    : str


    If ``string`` is longer than padding, it will be trimmed with ellipses

    Example
    -------
        ::

            left_string('A very long string', 10)
            # => 'A very ...'

            left_string('short', 10)
            # => 'short     '

    """
    if len(string) > padding:
        return '{}...'.format(string[0:padding-3])
    if len(string) == padding:
        return string
    if len(string) < padding:
        return '{string}{padding}'.format(
            string=string,
            padding=' '*(int(padding)-len(string))
        )
