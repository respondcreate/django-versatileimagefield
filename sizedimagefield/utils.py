def validate_centerpoint_tuple(tup):
    valid = True
    while valid == True:
        if len(tup) == 2:
            for x in tup:
                if x >= 0 and x <= 1:
                    pass
                else:
                    valid = False
            break
        else:
            valid = False
    return valid
