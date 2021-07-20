import sys

def main():
    sys.stdout.flush()
    tgt_lpar = sys.argv[1].split(',')
    user_name = sys.argv[2]
    # passwd = sys.argv[3]
    # email_address = sys.argv[4]
    
    sys.stdout.flush()

    # Get PVID of Nodes
    print(tgt_lpar)
    return 0


main()
