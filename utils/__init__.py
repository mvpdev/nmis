from csv_reader import CsvReader


def load_csv(model, path):
    csv_reader = CsvReader(path)
    for kwargs in csv_reader.iter_dicts():
        model.objects.create(**kwargs)
