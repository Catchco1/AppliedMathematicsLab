import argparse
#import callCenterSimulation

def main():
    parser = argparse.ArgumentParser(description='MTA Simulation')
    parser.add_argument('--dataFile', help='File containing data to feed into simulation')
    parser.parse_args()
    parser.print_help()
if __name__ == "__main__":
    main()

