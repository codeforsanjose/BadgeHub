import os
import json
from BadgeHub.utils import convert_to_dict


class MediaDimensions:
    def __init__(self, width_in: float, height_in: float, is_rectangle: bool, is_ellipse: bool = False):
        self.width_inches = width_in
        self.height_inches = height_in
        self.is_rectangle = is_rectangle
        self.is_ellipse = is_ellipse


class Printer:
    def __init__(self, short_name: str = None, model_name: str = None, manufacturer: str = None):
        self.short_name = short_name
        self.model_name = model_name
        self.manufacturer = manufacturer

    def __str__(self):
        return '{} : {} : {}'.format(self.manufacturer, self.short_name, self.model_name)


class Media:
    def __init__(self, cups_id: str, label: str, dimens: MediaDimensions):
        self.cups_id = cups_id
        self.label = label
        self.dimens = dimens

    def __eq__(self, other):
        if isinstance(other, Media):
            return self.cups_id == other.cups_id and self.label == other.label
        return False

    def __str__(self):
        return '{} : {}'.format(self.cups_id, self.label)


def cups_dimens_to_cm(dimens: str) -> MediaDimensions:
    """
    :param dimens: a string containing the CUPS dimensions. eg: '  "2.88 4.32 150.24 182.16"'
    :return: an instance of MediaDimensions containing the provided dimensions as inches
    """

    # ImageableArea section
    # the order is: Left, Top, Right, Bottom
    # the numbers are in 1/72nd of an inch
    CUPS_IMAGEABLE_UNITS = 1 / 72
    dimens = dimens.replace('"', '').strip().split(' ')
    width = (float(dimens[2]) - float(dimens[0])) * CUPS_IMAGEABLE_UNITS
    height = (float(dimens[3]) - float(dimens[1])) * CUPS_IMAGEABLE_UNITS

    return MediaDimensions(width_in=round(width, 2), height_in=round(height, 2), is_rectangle=True)


def ppd_to_media_sizes(path_to_ppd_file: str, printer_short_name : str):
    """
    Parse a given Cups ppd file and return a list of paper sizes, with human-friendly labels.

    The file will contain lines of text which should contain the media descriptors.

    Example of what we're looking for:
    *ImageableArea w79h252.1/30320 Address: "4.32 4.32 76.08 235.44"
                   ^         ^               ^---------------------^---dimensions, in 1/72nd of an inch
                   ^         ^------------^----------------------------media name
                   ^--------^------------------------------------------media identifier

    :param path_to_ppd_file: the path to the ppd file to be parsed, eg: "lw450t.ppd"
    :return: Dict:
    """

    printer_info = Printer(short_name=short_printer_name)
    page_sizes = {}
    with open(path_to_ppd_file, 'r') as ppd_file:
        for line in ppd_file:
            if line.startswith('*ModelName:'):
                printer_info.model_name = line.split(':')[1].replace('"', '').strip()
            if line.startswith('*Manufacturer:'):
                line = line.split(':')[1]
                printer_info.manufacturer = line.replace('"', '').strip()
            if line.startswith('*ImageableArea'):
                t = line.split('/', 1)
                cups_id = t[0].split(' ')[1]  # grab the identifier, eg: "w102h252"
                media_details = t[1].split(':')
                label = media_details[0]  # grab the name, eg: "30321 Large Address"
                printable_dimensions = media_details[1]
                dimens = cups_dimens_to_cm(printable_dimensions)
                page_sizes[cups_id] = Media(cups_id=cups_id, label=label, dimens=dimens)

    print('found {} media types'.format(len(page_sizes)))
    return {'printer': printer_info, 'media': page_sizes}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=
                                     'Media Size Generator: produce a list of page sizes from Cups ppd files.')
    parser.add_argument('--dir', help='directory containing ppd files')
    parser.add_argument('--outdir', default=os.getcwd(), help='the directory where the output JSON should be saved')
    args = parser.parse_args()

    ppd_directory = args.dir
    output_directory = args.outdir
    print('saving output to: {}'.format(output_directory))

    printers_info = {}
    for file in os.listdir(ppd_directory):
        if file.lower().endswith(".ppd"):
            pf = os.path.join(ppd_directory, file)
            print('found ppd file at {}'.format(pf))

            short_printer_name = str(os.path.basename(file).split('.')[0])
            ppd_output = ppd_to_media_sizes(pf, printer_short_name=short_printer_name)

            media_as_json = json.dumps(ppd_output['media'], sort_keys=True, default=convert_to_dict, indent=2)
            outfile = os.path.join(output_directory, short_printer_name+'.json')
            with open(outfile, 'w') as f:
                f.write(media_as_json)

            printers_info[short_printer_name] = ppd_output['printer']

    print('Finished parsing {} ppd files'.format(len(printers_info)))

    printers_output_file = os.path.join(output_directory, 'printers.json')
    media_as_json = json.dumps(printers_info, sort_keys=True, default=convert_to_dict, indent=2)
    print('saving printer info at {}'.format(printers_output_file))
    with open(printers_output_file, 'w') as file:
        file.write(media_as_json)
