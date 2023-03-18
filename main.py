import requests, json, argparse, sys, socket
from netaddr import *
import time

class colors:
	blue = "\033[1;34m"
	normal = "\033[0;00m"
	red = "\033[1;31m"
	bold = '\033[1m'

def format_ip(ip):
	obj = ip.strip().split('.')
	for x, y in enumerate(obj):	
		obj[x] = y.split('/')[0].lstrip('0')
		if obj[x] in ['', None]:
			obj[x] = '0'
	return '.'.join(obj)

def rdap_query(query, output):
	for i in query:
		try:
			r = requests.get("http://rdap.arin.net/registry/ip/{}".format(i))
			rdap = r.json()
			name = rdap["name"].title()
			start_address = format_ip(rdap["startAddress"])
			end_address = format_ip(rdap["endAddress"])
			net_range = "{}-{}".format(start_address, end_address)
			cidr = iprange_to_cidrs(start_address, end_address)[0]
			org = rdap["entities"][0]["vcardArray"][1][1][3]
			handle = rdap["entities"][0]["handle"]
			address = rdap["entities"][0]["vcardArray"][1][2][1]["label"].replace('\n', ', ')
			raw = json.dumps(rdap, sort_keys=True, indent=4, separators=(',', ': '))

		except KeyError as e:
			print("{}Error retrieving Whois for '{}'. Ensure you have provided a valid IP address{}".format(colors.red, i, colors.normal))
			continue

		if output == "raw":
			print("\n{} {} ({}) {}\n\n{}".format("-" * 20, name, i, "-" * 20, raw))
		elif output == "clean":
			print(cidr)
		else: #verbose
			print("\n{title} ({source}) {dash}\n  Name/Handle: {name}/{handle}\n  Net Range: {net_range}\n  CIDR: {cidr}\n  Organization: {org}\n  Address: {address}\n".format(title="{}{}{}".format(colors.bold, org, colors.normal), source=i, dash="{}{}{}".format(colors.blue, "-" * 40, colors.normal), name=name, handle=handle, net_range=net_range, cidr=cidr, org=org, address=address))


def main():
        parser = argparse.ArgumentParser()
        querygroup = parser.add_argument_group(title="Search")
        querygroup.add_argument('query', nargs='?', help='IP address or domain name to query')
        querygroup.add_argument('-f', metavar='file', nargs='?', help="A new line delimited file containing IP addresses or domain names")
        querygroup.add_argument('-r', action='store_true', help="Retrieve IP address for given domain(s)")
        outgroup = parser.add_mutually_exclusive_group()
        outgroup.add_argument('--clean', action='store_true', help="Print CIDRs from results")
        outgroup.add_argument('--raw', action='store_true', help="Print raw RDAP results as JSON")

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args()

        if not args.query and not args.f:
                print("Error")
                sys.exit(1)

        query = []
        if args.query:
                query.append(args.query)
        if args.f:
                with open(args.f) as f:
                        for line in f.readlines():
                                query.append(line.rstrip())

        if args.r:
                for i in query:
                        print(socket.gethostbyname(i.replace("http://", "").replace("https://", "").split('/')[0]))
        else:
                if args.raw:
                        rdap_query(query, "raw")
                elif args.clean:
                        rdap_query(query, "clean")
                else:
                        rdap_query(query, "verbose")

if __name__ == '__main__':
	try:
		main()
	except AddrFormatError as e:
		print("{}{}{}".format(colors.red, str(e).capitalize(), colors.normal))
	except Exception as e:
		print("{}{}{}".format(colors.red, e, colors.normal))
time.sleep(30)
