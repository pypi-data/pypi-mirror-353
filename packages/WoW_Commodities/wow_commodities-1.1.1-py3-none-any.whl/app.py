import argparse
import os
import sys
from rich.console import Console
from src.get_commodities import get_commodities
from src.get_token import get_token
from src.region_locale import region_locale
from src.process_data import process_data

console = Console()

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='wow-commodities',
        description=('Retrieve auction house commodities data from '
                     'a selected region.'),
        epilog=('This application comes with no warrant of any kind. '
        'Use at your own risk.')
    )
    parser.add_argument('id', help=('Client ID from Blizzard API Access.'),
                    type=str)
    parser.add_argument('secret', help=('Client Secret from Blizzard '
                                        'API Access.'),
                    type=str)
    parser.add_argument('path', help=('Path of file to save the data in '
                    '(e.g: C:\\User\\username\\Downloads\\data.csv.xz).'),
                    type=str)
    parser.add_argument('-r','--region',
                        help='Region to retrieve data from. Default to us.',
                        choices=['us', 'eu', 'kr', 'tw', 'cn'],
                        default='us', type=str)
    parser.add_argument('-l','--locale',
                        help=('Locale for the specified region. '
                              'Default to en_US.'),
                        choices=[
                            'en_US', 'es_MX', 'pt_BR', 'en_GB',
                            'es_ES', 'fr_FR', 'ru_RU', 'de_DE',
                            'pt_PT', 'it_IT', 'ko_KR', 'zh_TW',
                            'zh_CN'],
                        default='en_US',
                    type=str)
    args = parser.parse_args()

    if args.locale not in region_locale[args.region]:
        sys.exit(f'Region {args.region} does not accept {args.locale} locale. '
             f'Please choose between {region_locale[args.region]}.')
    
    if args.region == 'cn':
        URL = 'https://gateway.battlenet.com.cn/data/wow/'
    else:
        URL = f'https://{args.region}.api.blizzard.com/data/wow/'
    LOCALE: str = f'{args.locale}'
    TOKEN: str = get_token(args.id, args.secret, args.region)

    if os.path.splitext(args.path)[1] != 'xz':
        args.path += ".xz"

    with console.status(
        "[bold]Downloading data...[/bold]", spinner="dots2"
        ):
        data = get_commodities(URL, LOCALE, TOKEN, args.path)
    console.print("[bold green]Done![/bold green]")

    with console.status(
        "[bold]Generating table...[/bold]", spinner="dots2"
        ):
        if data:
            process_data(data, args.path)
    console.print("[bold green]Done![/bold green]")

if __name__ == "__main__":
    main()
