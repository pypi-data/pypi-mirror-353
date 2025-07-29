import sys
import pandas as pd

def process_data(data, path):
    id: list[int] = []
    item: list[int] = []
    quantity: list[int] = []
    unit_price: list[int] = []
    time_left: list[str] = []
    for i in range(len(data['auctions'])):
        id.append(data['auctions'][i]['id'])
        item.append(data['auctions'][i]['item']['id'])
        quantity.append(data['auctions'][i]['quantity'])
        unit_price.append(data['auctions'][i]['unit_price'])
        time_left.append(data['auctions'][i]['time_left'])

    try:
        pd.DataFrame(
            {'ID': id,
            'Item': item,
            'Quantity': quantity,
            'Unit Price': unit_price,
            'Time Left': time_left}
        ).to_csv(path, index=False)
    except PermissionError:
        sys.exit('Cannot save file. Permission denied.')
