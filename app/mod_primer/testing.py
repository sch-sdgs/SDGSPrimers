
import json
import pprint
def convert_json_to_choices(json_file):
    pp = pprint.PrettyPrinter(indent=2)
    with open(json_file) as json_data:
        all_data = json.load(json_data)

    result = []
    for i in all_data:
        choices = tuple()
        for choice in all_data[i]:
            choices = ((choice["value"],choice["label"]),)+choices
        group = (i,(choices))
        result.append(group)

    final = tuple(result)
    pp.pprint(final)
    return final


convert_json_to_choices('/home/dnamdp/wc/SDGSPrimers/app/resources/5_prime_mods.json')