def left_string(string, padding):
    if len(string) > padding:
        return '{}...'.format(string[0:padding-3])
    if len(string) == padding:
        return string
    if len(string) < padding:
        return '{string}{padding}'.format(
            string=string,
            padding=' '*(padding-len(string))
        )
