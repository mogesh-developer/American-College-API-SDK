def parse(model, data):

    return model.from_dict(data)


def parse_many(model, data):

    return [
        model.from_dict(x)
        for x in data
    ]